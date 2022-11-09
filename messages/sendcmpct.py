from utils.byte import reverse


def parse_sendcmpct(s):
    is_cmpctblock = bool(s[20])
    cmpct_number = int.from_bytes(s[21:], "little")

    return is_cmpctblock, cmpct_number
