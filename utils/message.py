from utils.byte import reverse, int_hex, ip_hex, nonce_hex, varint
from utils.hash import double256
from utils.log import log_print
from binascii import b2a_hex, a2b_hex
from time import time


def create_header(msg, type):
    length_type = '{:\x00<%i}' % 12
    type_msg = b2a_hex(length_type.format(type).encode()).decode()

    length_msg = len(a2b_hex(msg))

    checksum = b2a_hex(double256(msg)[:4]).decode()

    return type_msg + reverse(int_hex(length_msg, 4)) + checksum


def verify_header(s):
    length = int(reverse(b2a_hex(s[12:16])), 16)
    checksum = s[16:20]
    is_length = length == len(s[20:])
    is_checksum = checksum == double256(b2a_hex(s[20:]))[:4]
    return is_length and is_checksum


def pong(s):
    return b2a_hex(s[20:]).decode()


def verack():
    return ''


def version(int_version, host, port, agent):
    VERSION = reverse(int_hex(int_version, 4))
    SERVICE = reverse(int_hex(1, 8))
    EPOCH = int_hex(int(time()), 8)
    RECV_ADDR = ip_hex(host)
    RECV_PORT = int_hex(port, 2)
    NODE_ADDR = int_hex(0, 16)
    NODE_PORT = int_hex(0, 2)
    NONCE = nonce_hex()
    LENGTH_USERAGENT = int_hex(len(agent), 1)
    USERAGENT = b2a_hex(agent).decode()
    START_HEIGHT = reverse(int_hex(1, 4))
    RELAY = reverse(int_hex(1, 1))

    return VERSION + SERVICE + EPOCH + SERVICE + RECV_ADDR + RECV_PORT + \
        SERVICE + NODE_ADDR + NODE_PORT + NONCE + LENGTH_USERAGENT + \
        USERAGENT + START_HEIGHT + RELAY


def inv(s):
    length_inv = varint(s[20:])

    for i in range(length_inv):
        inv = s[21 + 36*i: 21 + 36*(i+1)]

        inv_type = inv[:4].rstrip(b'\00')
        if inv_type == b'\x01':
            inv_type = 'MSG_TX'
        elif inv_type == b'\x02':
            inv_type = 'MSG_BLOCK'
        elif inv_type == b'\x03':
            inv_type = 'MSG_FILTERED_BLOCK'
        elif inv_type == b'\x04':
            inv_type = 'MSG_CMPCT_BLOCK'
        else:
            inv_type = 'ERROR'

        inv_content = reverse(b2a_hex(inv[4:]))
        log_print('inv #%i' % (i+1), "%s -> %s" % (inv_type, inv_content))
