from hashlib import sha256
from binascii import a2b_hex


def double256(s):
    return sha256(sha256(s).digest()).digest()
