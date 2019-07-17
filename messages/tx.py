from utils.hash import double256
from binascii import b2a_hex
from utils.byte import reverse
from utils.log import log_print

def parse_tx(s):
    content = s[20:]
    tx_hash = double256(b2a_hex(content))
    txid = reverse(b2a_hex(tx_hash))

    log_print('new tx', txid)