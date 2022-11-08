from time import time, strftime, localtime


def create_version(int_version, host_port, agent):
    host, port = host_port

    VERSION = (int_version).to_bytes(4, byteorder="little")
    SERVICE = (1).to_bytes(8, byteorder="little")
    EPOCH = (int(time())).to_bytes(9, byteorder="little")
    RECV_ADDR = IP2b(host)
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
    version = int.from_bytes(s[20:24], "little")
    epoch = int.from_bytes(s[32:40], "little")

    date = strftime("%d/%m/%Y %H:%M:%S", localtime(epoch))

    len_agent = s[100]
    agent = s[101 : 101 + len_agent].decode()

    return agent, date, version


def IP2b(s):
    ip_s = s.split(".")

    ip_i = 0
    for i in range(len(ip_s)):
        ip_i += int(ip_s[i]) * 2 ** (24 - 8 * i)

    ip_i = 0xFFFF00000000 + ip_i

    return (ip_i).to_bytes(16, "big")
