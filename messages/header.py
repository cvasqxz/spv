from utils.hash import double256
from utils.byte import reverse


def create_header(msg, type):
    type_msg = ("{:\x00<%i}" % 12).format(type).encode()
    length_msg = (len(msg)).to_bytes(4, "little")
    checksum = double256(msg)[:4]

    return type_msg + length_msg + checksum


def verify_header(s):
    length = int(reverse(s[12:16]), 16)
    checksum = s[16:20]

    is_length = length == len(s[20:])
    is_checksum = checksum == double256(s[20:])[:4]

    return is_length and is_checksum
