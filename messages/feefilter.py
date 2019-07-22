from utils.byte import reverse
from utils.log import log_print


def parse_feefilter(s):
    min_relay_fee = int(reverse(s[20:]), 16)
    log_print('min fee', '%.8f BTC/kb' % (min_relay_fee/1e8))
