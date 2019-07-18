from binascii import b2a_hex, a2b_hex
from utils.hash import double256
from utils.byte import reverse, int_hex

def create_header(msg, type):
    length_type = '{:\x00<%i}' % 12
    type_msg = b2a_hex(length_type.format(type).encode()).decode()

    length_msg = len(a2b_hex(msg))

    checksum = b2a_hex(double256(msg)[:4]).decode()

    return type_msg + reverse(int_hex(length_msg, 4)) + checksum


def verify_header(s):
    length = int(reverse(s[12:16]), 16)
    checksum = s[16:20]
    is_length = length == len(s[20:])
    is_checksum = checksum == double256(s[20:])[:4]
    return is_length and is_checksum
