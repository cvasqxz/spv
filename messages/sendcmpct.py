from utils.byte import reverse


def parse_sendcmpct(s):
    is_cmpctblock = bool(s[20])
    cmpct_number = int(reverse(s[21:]), 16)

    return is_cmpctblock, cmpct_number
