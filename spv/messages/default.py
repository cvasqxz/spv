def pong(s):
    return s


def verack():
    return b""


def parse_feefilter(s):
    return int.from_bytes(s, "little")


def create_feefilter(i):
    return (i).to_bytes(8, byteorder="little")


def parse_sendcmpct(s):
    is_cmpctblock = bool(s)
    cmpct_number = int.from_bytes(s[1:], "little")

    return is_cmpctblock, cmpct_number
