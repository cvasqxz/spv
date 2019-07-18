from utils.hash import double256
from binascii import b2a_hex
from utils.byte import reverse
from utils.log import log_print

def parse_tx(s):
    tx_hash = double256(s[20:])
    txid = reverse(tx_hash)

    log_print('new tx', txid)