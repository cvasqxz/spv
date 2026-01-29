from spv.utils.hash import double256


def create_header(type, msg):
    # Command name: 12 bytes, null-padded
    type_bytes = type.encode()
    type_msg = type_bytes + b'\x00' * (12 - len(type_bytes))

    length_msg = (len(msg)).to_bytes(4, "little")
    checksum = double256(msg)[:4]

    return type_msg + length_msg + checksum


def verify_header(s):
    length = int.from_bytes(s[12:16], "little")
    checksum = s[16:20]

    is_length = length == len(s[20:])
    is_checksum = checksum == double256(s[20:])[:4]

    return is_length and is_checksum
