from utils.byte import reverse, int_hex, ip_hex, nonce_hex
from time import time
from binascii import b2a_hex

def create_version(int_version, host, port, agent):
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
