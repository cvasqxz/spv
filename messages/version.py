from utils.byte import reverse, int_hex, ip_hex
from utils.log import log_print
from time import time, strftime, localtime
from binascii import b2a_hex

def create_version(int_version, host_port, agent):
    host, port = host_port
    
    VERSION = reverse(int_hex(int_version, 4))
    SERVICE = reverse(int_hex(1, 8))
    EPOCH = reverse(int_hex(int(time()), 8))
    RECV_ADDR = ip_hex(host)
    RECV_PORT = int_hex(port, 2)
    NODE_ADDR = int_hex(0, 16)
    NODE_PORT = int_hex(0, 2)
    NONCE = int_hex(0, 8)
    LENGTH_USERAGENT = int_hex(len(agent), 1)
    USERAGENT = b2a_hex(agent).decode()
    START_HEIGHT = reverse(int_hex(1, 4))
    RELAY = reverse(int_hex(1, 1))

    return VERSION + SERVICE + EPOCH + SERVICE + RECV_ADDR + RECV_PORT + \
        SERVICE + NODE_ADDR + NODE_PORT + NONCE + LENGTH_USERAGENT + \
        USERAGENT + START_HEIGHT + RELAY

def parse_version(s):
    message = s[20:]

    version = int(reverse(b2a_hex(message[0:4])), 16)

    epoch = int(reverse(b2a_hex(message[12:20])), 16)
    date = strftime('%d/%m/%Y %H:%M:%S', localtime(epoch))

    len_agent = message[80]
    agent = message[81:81+len_agent].decode()

    log_print("node agent", agent)
    log_print("node time", date)
    log_print("node protocol version", version)
    