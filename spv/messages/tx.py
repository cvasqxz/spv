from spv.utils.hash import double256
from spv.utils.byte import parse_varint

from binascii import hexlify


def get_satoshis(json_tx):
    return sum([s["satoshis"] for s in json_tx["outputs"]]) * 1e-8


def extract_tx(tx):
    inputs = []
    outputs = []
    total_satoshis = 0
    pointer = 4

    version = int.from_bytes(tx[:4], "little")

    segwit_flag = tx[pointer : pointer + 2] == b"\x00\x01"

    if segwit_flag:
        pointer += 2

    ins_count, bytes_read = parse_varint(tx[pointer:])
    pointer += bytes_read

    for _ in range(ins_count):
        utxo = tx[pointer : pointer + 32][::-1]
        pointer += 32

        vout = int.from_bytes(tx[pointer : pointer + 4], "little")
        pointer += 4

        len_sigscript, bytes_read = parse_varint(tx[pointer:])
        pointer += bytes_read

        sigscript = tx[pointer : pointer + len_sigscript]
        pointer += len_sigscript

        sequence = tx[pointer : pointer + 4]
        pointer += 4

        inputs.append(
            {
                "utxo": bytes.decode(hexlify(utxo)),
                "vout": vout,
                "scriptsig": bytes.decode(hexlify(sigscript)),
                "sequence": bytes.decode(hexlify(sequence)),
            }
        )

    outs_count, bytes_read = parse_varint(tx[pointer:])
    pointer += bytes_read

    for n in range(outs_count):
        satoshis = int.from_bytes(tx[pointer : pointer + 8], "little")
        total_satoshis += satoshis
        pointer += 8

        len_scriptpubkey, bytes_read = parse_varint(tx[pointer:])
        pointer += bytes_read

        scriptpubkey = tx[pointer : pointer + len_scriptpubkey]
        pointer += len_scriptpubkey

        outputs.append(
            {
                "n": n,
                "satoshis": satoshis,
                "redeemscript": bytes.decode(hexlify(scriptpubkey))
            }
        )

    vsize = pointer + 4

    if segwit_flag:
        for input_index in range(ins_count):

            witnesses_count, bytes_read = parse_varint(tx[pointer:])
            pointer += bytes_read

            programs = []

            for _ in range(witnesses_count):
                len_program, bytes_read = parse_varint(tx[pointer:])
                pointer += bytes_read

                program = tx[pointer : pointer + len_program]
                pointer += len_program

                programs.append(bytes.decode(hexlify(program)))

            inputs[input_index]["witnesses"] = programs

    locktime = int.from_bytes(tx[pointer:], "little")


    if segwit_flag:
        simple_tx = tx[0:4] + tx[6:(vsize - 4)] + tx[-4:]
        tx_hash = double256(simple_tx)
    else:
        tx_hash = double256(tx)

    txid = bytes.decode(hexlify(tx_hash[::-1]))


    json_tx = {
        "size": len(tx),
        "vsize": vsize,
        "txid": txid,
        "version": version,
        "inputs": inputs,
        "outputs": outputs,
        "locktime": locktime,
    }

    return json_tx