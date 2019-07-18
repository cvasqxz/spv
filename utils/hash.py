from hashlib import sha256
from binascii import a2b_hex


def double256(s):
    if type(s) is str:
        bs = a2b_hex(s)
    elif type(s) is bytes:
        bs = s
    else:
        return b''
        
    return sha256(sha256(bs).digest()).digest()
