from utils.byte import reverse


def parse_feefilter(s):
    return int.from_bytes(s[20:], "little")
