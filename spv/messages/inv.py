from spv.utils.byte import parse_varint, create_varint

inv_types = {
    0x01: "MSG_TX",
    0x02: "MSG_BLOCK",
    0x03: "MSG_FILTERED_BLOCK",
    0x04: "MSG_CMPCT_BLOCK",
}

# https://www.geeksforgeeks.org/python-program-to-swap-keys-and-values-in-dictionary/
reversed_inv_types = dict([(value, key) for key, value in inv_types.items()])


def parse_inv(s):
    length_inv, bytes_read = parse_varint(s)
    inv_array = []

    for i in range(length_inv):
        inv = s[bytes_read + 36 * i : bytes_read + 36 * (i + 1)]
        inv_type = int.from_bytes(inv[0:4], "little")
        inv_type = inv_types[inv_type]

        inv_content = inv[4:][::-1]

        inv_array.append({"type": inv_type, "content": inv_content})

    return inv_array


def create_invs(inv_array):
    # ESTO ESTA MAL, ES UN VARINT
    s = create_varint(len(inv_array))

    for inv in inv_array:
        inv_code = reversed_inv_types[inv["type"]]

        # https://github.com/bitcoin/bips/blob/master/bip-0144.mediawiki
        if inv["type"] in ["MSG_TX", "MSG_BLOCK"]:
            inv_code += 1 << 30

        s += inv_code.to_bytes(4, byteorder="little")
        s += inv["content"][::-1]

    return s
