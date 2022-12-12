from time import time, strftime, localtime
from utils.byte import ip2b


def create_version(int_version, host_port, agent):
    host, port = host_port

    VERSION = (int_version).to_bytes(4, byteorder="little")
    SERVICE = (1).to_bytes(8, byteorder="little")
    EPOCH = (int(time())).to_bytes(9, byteorder="little")
    RECV_ADDR = ip2b(host)
    RECV_PORT = (port).to_bytes(2, byteorder="big")
    NODE_ADDR = (0).to_bytes(16, byteorder="big")
    NODE_PORT = (0).to_bytes(2, byteorder="big")
    NONCE = (0).to_bytes(8, byteorder="big")
    LENGTH_USERAGENT = (len(agent)).to_bytes(1, byteorder="big")
    USERAGENT = agent.encode()
    START_HEIGHT = (1).to_bytes(4, byteorder="little")

    RELAY = b"\x01"

    return (
        VERSION
        + SERVICE
        + EPOCH
        + SERVICE
        + RECV_ADDR
        + RECV_PORT
        + SERVICE
        + NODE_ADDR
        + NODE_PORT
        + NONCE
        + LENGTH_USERAGENT
        + USERAGENT
        + START_HEIGHT
        + RELAY
    )


def parse_version(s):
    version = int.from_bytes(s[0:4], "little")
    epoch = int.from_bytes(s[12:20], "little")

    date = strftime("%d/%m/%Y %H:%M:%S", localtime(epoch))

    len_agent = s[80]
    agent = bytes.decode(s[81 : 81 + len_agent])

    return agent, date, version
