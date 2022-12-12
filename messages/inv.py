from utils.byte import varint


def parse_inv(s):

    inv_types = {
        0x01: "MSG_TX",
        0x02: "MSG_BLOCK",
        0x03: "MSG_FILTERED_BLOCK",
        0x04: "MSG_CMPCT_BLOCK",
        0x40000001: "MSG_WITNESS_TX",
        0x40000002: "MSG_WITNESS_BLOCK",
    }

    length_inv, bytes_read = varint(s)

    inv_array = []

    for i in range(length_inv):
        inv = s[bytes_read + 36 * i : bytes_read + 36 * (i + 1)]
        inv_type = int.from_bytes(inv[0:4], "little")
        inv_type = inv_types[inv_type]

        if inv_type == "MSG_TX":
            inv_type = "MSG_WITNESS_TX"

        inv_content = inv[4:][::-1]

        inv_array.append({"type": inv_type, "content": inv_content})

    return inv_array, s
