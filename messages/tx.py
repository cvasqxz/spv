from utils.hash import double256
from utils.byte import varint

from binascii import hexlify


def get_satoshis(json_tx):
    return sum([s["satoshis"] for s in json_tx["outputs"]]) * 1e-8


def extract_tx(tx):
    tx_hash = double256(tx)
    txid = tx_hash[::-1]

    version = int.from_bytes(tx[:4], "little")

    ins_count, bytes_read = varint(tx[4:])
    pointer = 4 + bytes_read

    inputs = []

    for _ in range(ins_count):
        txid = tx[pointer : pointer + 32][::-1]
        pointer += 32

        n = int.from_bytes(tx[pointer : pointer + 4], "little")
        pointer += 4

        len_sigscript, bytes_read = varint(tx[pointer:])
        pointer += bytes_read

        sigscript = tx[pointer : pointer + len_sigscript]
        pointer += len_sigscript

        sequence = tx[pointer : pointer + 4]
        pointer += 4

        inputs.append(
            {
                "txid": txid,
                "n": n,
                "sigscript": hexlify(sigscript),
                "sequence": hexlify(sequence),
            }
        )

    outs_count, bytes_read = varint(tx[pointer:])
    pointer += bytes_read

    outputs = []
    total_satoshis = 0

    for _ in range(outs_count):
        satoshis = int.from_bytes(tx[pointer : pointer + 8], "little")
        total_satoshis += satoshis
        pointer += 8

        len_scriptpubkey, bytes_read = varint(tx[pointer:])
        pointer += bytes_read

        scriptpubkey = tx[pointer : pointer + len_scriptpubkey]
        pointer += len_scriptpubkey

        outputs.append({"satoshis": satoshis, "redeemscript": hexlify(scriptpubkey)})

    locktime = int.from_bytes(tx[pointer:], "little")

    json_tx = {
        "version": version,
        "inputs": inputs,
        "outputs": outputs,
        "locktime": locktime,
        "total_satoshis": total_satoshis,
    }

    return txid, tx
