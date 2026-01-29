from spv.utils.hash import double256
from spv.utils.byte import parse_varint, reverse_bytes, to_hex


def parse_tx(tx):
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
        utxo = reverse_bytes(tx[pointer : pointer + 32])
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
                "utxo": to_hex(utxo),
                "vout": vout,
                "scriptsig": to_hex(sigscript),
                "sequence": to_hex(sequence),
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
                "redeemscript": to_hex(scriptpubkey)
            }
        )

    # Base size is the transaction size without witness data
    base_size = pointer + 4
    witness_start_pos = pointer

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

                programs.append(to_hex(program))

            inputs[input_index]["witnesses"] = programs

    # Locktime is always 4 bytes at the end
    locktime = int.from_bytes(tx[pointer:pointer+4], "little")
    pointer += 4

    # Calculate txid (hash of non-witness data)
    if segwit_flag:
        # Reconstruct tx without marker/flag and witness data for txid calculation
        # Format: version + inputs + outputs + locktime
        locktime_bytes = tx[pointer-4:pointer]
        simple_tx = tx[0:4] + tx[6:witness_start_pos] + locktime_bytes
        tx_hash = double256(simple_tx)
    else:
        tx_hash = double256(tx)

    txid = to_hex(reverse_bytes(tx_hash))

    # Calculate vsize (virtual size for fee calculation)
    # For SegWit: vsize = (base_size * 3 + total_size) / 4
    # For legacy: vsize = size
    if segwit_flag:
        total_size = pointer
        vsize = (base_size * 3 + total_size) // 4
    else:
        vsize = base_size

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