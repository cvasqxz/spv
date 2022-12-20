from time import time, strftime, localtime
from spv.utils.byte import ip2b
from binascii import hexlify

SERVICES = {
    "NODE_NETWORK": (1 << 0),
    "NODE_BLOOM": (1 << 2),
    "NODE_WITNESS": (1 << 3),
    "NODE_COMPACT_FILTERS": (1 << 6),
    "NODE_NETWORK_LIMITED": (1 << 10),
}


def create_version(int_version, host_port, agent):
    selected_services = SERVICES["NODE_NETWORK"]
    selected_services |= SERVICES["NODE_WITNESS"]
    selected_services |= SERVICES["NODE_NETWORK_LIMITED"]

    host, port = host_port

    VERSION = (int_version).to_bytes(4, byteorder="little")
    SERVICE = (selected_services).to_bytes(8, byteorder="little")
    EPOCH = (int(time())).to_bytes(9, byteorder="little")
    RECV_ADDR = ip2b(host)
    RECV_PORT = (port).to_bytes(2, byteorder="big")
    NODE_ADDR = (0).to_bytes(16, byteorder="big")
    NODE_PORT = (0).to_bytes(2, byteorder="big")
    NONCE = (0).to_bytes(8, byteorder="little")
    LENGTH_USERAGENT = (len(agent)).to_bytes(1, byteorder="little")
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
    services = int.from_bytes(s[4:12], "little")
    epoch = int.from_bytes(s[12:20], "little")

    node_services = []

    for tag in SERVICES:
        if SERVICES[tag] & services > 0:
            node_services.append(tag)

    date = strftime("%d/%m/%Y %H:%M:%S", localtime(epoch))

    len_agent = s[80]
    agent = bytes.decode(s[81 : 81 + len_agent])

    return agent, ", ".join(node_services), version
