from binascii import a2b_hex, b2a_hex


def b2a(s):
    return b2a_hex(s).decode()


def reverse(s):
    if type(s) is str:
        bs = a2b_hex(s)
    elif type(s) is bytes:
        bs = s
    else:
        return b''

    return b2a(bs[::-1])


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


def hex_ip(s):
    ipv = s.strip(b'\x00')
    ip = str(ipv[-4]) + '.' + str(ipv[-3]) + '.' + \
        str(ipv[-2]) + '.' + str(ipv[-1])
    return ip


def varint(s):
    if s[0] == 253:
        return int(reverse(s[1:4]), 16) - 1, 4
    elif s[0] == 254:
        return int(reverse(s[1:6]), 16) - 1, 6
    elif s[0] == 255:
        return int(reverse(s[1:10]), 16) - 1, 10
    else:
        return s[0], 1
