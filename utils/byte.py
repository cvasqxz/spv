from binascii import a2b_hex, b2a_hex
from random import randint


def reverse(s):
    return b2a_hex(a2b_hex(s)[::-1]).decode()


def int_hex(s, length):
    length_bytes = '{:0%ix}' % (length*2)
    return length_bytes.format(s)


def ip_hex(s):
    ip_s = s.split('.')

    ip_i = 0
    for i in range(len(ip_s)):
        ip_i += int(ip_s[i])*2**(24 - 8*i)

    ip_i = 0xffff00000000 + ip_i

    return int_hex(ip_i, 16)

def varint(s):
    if s[0] == 253:
        return int(b2a_hex(s[1:4]), 16)
    elif s[0] == 254:
        return int(b2a_hex(s[1:6]), 16)
    elif s[0] == 255:
        return int(b2a_hex(s[1:10]), 16)
    else:
        return s[0]
