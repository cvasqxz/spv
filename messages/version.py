from utils.byte import reverse, int_hex, ip_hex, b2a
from utils.log import log_print
from time import time, strftime, localtime


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
    USERAGENT = b2a(agent)
    START_HEIGHT = reverse(int_hex(1, 4))
    RELAY = reverse(int_hex(1, 1))

    return VERSION + SERVICE + EPOCH + SERVICE + RECV_ADDR + RECV_PORT + \
        SERVICE + NODE_ADDR + NODE_PORT + NONCE + LENGTH_USERAGENT + \
        USERAGENT + START_HEIGHT + RELAY

def parse_version(s):
    version = int(reverse(s[20:24]), 16)

    epoch = int(reverse(s[32:40]), 16)
    date = strftime('%d/%m/%Y %H:%M:%S', localtime(epoch))

    len_agent = s[100]
    agent = s[101:101+len_agent].decode()

    log_print("node agent", agent)
    log_print("node time", date)
    log_print("node protocol version", version)
    