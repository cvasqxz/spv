from hashlib import sha256


def double256(s):
    return sha256(sha256(s).digest()).digest()
