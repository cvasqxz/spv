from binascii import b2a_hex


def pong(s):
    return b2a_hex(s[20:]).decode()


def verack():
    return ''
