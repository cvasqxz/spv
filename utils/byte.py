from binascii import a2b_hex, b2a_hex


def b2a(s):
    return bytes.decode(b2a_hex(s))


def reverse(s):
    if type(s) is str:
        bs = a2b_hex(s)
    elif type(s) is bytes:
        bs = s
    else:
        return b""

    return b2a(bs[::-1])


def b2ip(s):
    ipv = s.strip(b"\x00")
    ip = str(ipv[-4]) + "." + str(ipv[-3]) + "." + str(ipv[-2]) + "." + str(ipv[-1])
    return ip


def ip2b(s):
    ip_s = s.split(".")

    ip_i = 0
    for i in range(len(ip_s)):
        ip_i += int(ip_s[i]) * 2 ** (24 - 8 * i)

    ip_i = 0xFFFF00000000 + ip_i

    return (ip_i).to_bytes(16, "big")


def varint(s):
    if s[0] < 0xFD:
        return s[0], 1

    off = 2 ** (s[0] - 0xFC)
    output = int.from_bytes(s[1 : 1 + off], "little")

    return output - 1, off + 2
