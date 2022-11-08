from utils.hash import double256
from utils.byte import reverse, varint, b2a


def extract_tx(s):
    tx = s[20:]

    tx_hash = double256(s[20:])
    txid = reverse(tx_hash)

    return txid, tx


def parse_tx(raw_tx):
    version = int.from_bytes(raw_tx[:4], "little")

    ins_count, bytes_read = varint(raw_tx[4:])
    pointer = 4 + bytes_read

    vin = []

    for _ in range(ins_count):
        txid = reverse(raw_tx[pointer : pointer + 32])
        pointer += 32

        n = int.from_bytes(raw_tx[pointer : pointer + 4], "little")
        pointer += 4

        len_sigscript, bytes_read = varint(raw_tx[pointer:])
        pointer += bytes_read

        sigscript = raw_tx[pointer : pointer + len_sigscript]
        pointer += len_sigscript

        sequence = raw_tx[pointer : pointer + 4]
        pointer += 4

        vin.append(
            {
                "txid": txid,
                "n": n,
                "sigscript": b2a(sigscript),
                "sequence": b2a(sequence),
            }
        )

    outs_count, bytes_read = varint(raw_tx[pointer:])
    pointer += bytes_read

    vout = []

    for _ in range(outs_count):
        satoshis = int.from_bytes(raw_tx[pointer : pointer + 8], "little")
        pointer += 8

        len_scriptpubkey, bytes_read = varint(raw_tx[pointer:])
        pointer += bytes_read

        scriptpubkey = raw_tx[pointer : pointer + len_scriptpubkey]
        pointer += len_scriptpubkey

        vout.append({"satoshis": satoshis, "redeemscript": b2a(scriptpubkey)})

    locktime = int.from_bytes(raw_tx[pointer:], "little")

    return {"version": version, "ins": vin, "outs": vout, "locktime": locktime}
