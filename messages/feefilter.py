from utils.byte import reverse


def parse_feefilter(s):
    return int(reverse(s[20:]), 16)