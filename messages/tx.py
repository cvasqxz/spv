from utils.hash import double256
from utils.byte import reverse, varint
from utils.log import log_print
from binascii import b2a_hex


def extract_tx(s):
    tx = s[20:]

    tx_hash = double256(s[20:])
    txid = reverse(tx_hash)

    tx_size = len(tx) / 1024

    log_print('tx', '%s (%.2f kb)' % (txid, tx_size))

    return txid, tx


def parse_tx(raw_tx):
    tx_dict = {}

    version = int(reverse(raw_tx[:4]), 16)
    tx_dict['version'] = version

    ins_count, bytes_read = varint(raw_tx[4:])
    pointer = 4 + bytes_read

    vin = []
    while ins_count > 0:
        vin_dict = {}
        txid = reverse(raw_tx[pointer:pointer + 32])
        pointer += 32
        n = int(reverse(raw_tx[pointer:pointer + 4]), 16)
        pointer += 4
        len_sigscript, bytes_read = varint(raw_tx[pointer:])
        pointer += bytes_read
        sigscript = raw_tx[pointer:pointer + len_sigscript]
        pointer += len_sigscript
        ins_count -= 1
        sequence = raw_tx[pointer: pointer + 4]
        pointer += 4

        vin_dict['txid'] = txid
        vin_dict['n'] = n
        vin_dict['sigscript'] = b2a_hex(sigscript).decode()
        vin_dict['sequence'] = b2a_hex(sequence).decode()

        vin.append(vin_dict)

    outs_count, bytes_read = varint(raw_tx[pointer:])
    pointer += bytes_read

    vout = []
    while outs_count > 0:
        vout_dict = {}
        satoshis = int(reverse(raw_tx[pointer:pointer + 8]), 16)
        pointer += 8
        len_scriptpubkey, bytes_read = varint(raw_tx[pointer:])
        pointer += bytes_read
        scriptpubkey = raw_tx[pointer:pointer + len_scriptpubkey]
        pointer += len_scriptpubkey
        outs_count -= 1

        vout_dict['satoshis'] = satoshis
        vout_dict['scriptpubkey'] = b2a_hex(scriptpubkey).decode()
        vout.append(vout_dict)

    locktime = int(reverse(raw_tx[pointer:]), 16)

    tx_dict['inputs'] = vin
    tx_dict['outputs'] = vout
    tx_dict['locktime'] = locktime

    return tx_dict
