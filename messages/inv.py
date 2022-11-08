from utils.byte import varint, reverse


def parse_inv(s):

    inv_types = {
        0x01: "MSG_TX",
        0x02: "MSG_BLOCK",
        0x03: "MSG_FILTERED_BLOCK",
        0x04: "MSG_CMPCT_BLOCK",
    }

    length_inv, bytes_read = varint(s[20:])

    inv_array = []

    for i in range(length_inv):
        inv = s[20 + bytes_read + 36 * i : 20 + bytes_read + 36 * (i + 1)]
        inv_type = int.from_bytes(inv[:4], "little")
        inv_type = inv_types[inv_type]

        inv_content = reverse(inv[4:])

        inv_array.append({"type": inv_type, "content": inv_content})

    return inv_array, s[20:]
