from spv.utils.byte import parse_varint, create_varint, reverse_bytes

inv_types = {
    0x01: "MSG_TX",
    0x02: "MSG_BLOCK",
    0x03: "MSG_FILTERED_BLOCK",
    0x04: "MSG_CMPCT_BLOCK",
    0x05: "MSG_WITNESS_TX",
    0x40000001: "MSG_WITNESS_TX",
    0x40000002: "MSG_WITNESS_BLOCK",
}

def parse_inv(s):
    length_inv, bytes_read = parse_varint(s)
    inv_array = []

    for i in range(length_inv):
        inv = s[bytes_read + 36 * i : bytes_read + 36 * (i + 1)]
        inv_type = int.from_bytes(inv[0:4], "little")
        inv_type = inv_types[inv_type]

        inv_content = reverse_bytes(inv[4:])

        inv_array.append({"type": inv_type, "content": inv_content})

    return inv_array
