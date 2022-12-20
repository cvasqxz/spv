def b2ip(s):
    ipv = s.strip(b"\x00")
    ip = ".".join([str(n) for n in ipv[-4:]])
    return ip


def ip2b(s):
    ip_s = s.split(".")

    ip_i = 0
    for i in range(len(ip_s)):
        ip_i += int(ip_s[i]) * 2 ** (24 - 8 * i)

    ip_i = 0xFFFF00000000 + ip_i

    return (ip_i).to_bytes(16, "big")


def parse_varint(s):
    if s[0] < 0xFD:
        return s[0], 1

    if s[0] == 0xFD:
        return int.from_bytes(s[1:4], "little"), 3

    if s[0] == 0xFE:
        return int.from_bytes(s[1:5], "little"), 5

    if s[0] == 0xFF:
        return int.from_bytes(s[1:9], "little"), 9


def create_varint(i):
    if i < 0xFD:
        return i.to_bytes(1, byteorder="little")

    if i >= 0xFD and i <= 0xFFFF:
        return b"\xFD" + i.to_bytes(3, byteorder="little")

    if i > 0xFFFF and i <= 0xFFFFFFFF:
        return b"\xFE" + i.to_bytes(5, byteorder="little")

    if i > 0xFFFFFFFF:
        return b"\xFF" + i.to_bytes(9, byteorder="little")
