from utils.hash import double256
from binascii import b2a_hex
from utils.byte import reverse
from utils.log import log_print

def parse_tx(s):
    tx = b2a_hex(s[20:]).decode()

    tx_hash = double256(s[20:])
    txid = reverse(tx_hash)

    tx_size = len(tx) / 1024

    log_print('new tx', '%s (%.2f kb)' % (txid, tx_size))

    return txid, tx