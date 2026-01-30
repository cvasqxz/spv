from time import time, localtime
from spv.utils.byte import ip2b, b2ip
import random

SERVICES = {
    "NODE_NETWORK": (1 << 0),
    "NODE_BLOOM": (1 << 2),
    "NODE_WITNESS": (1 << 3),
    "NODE_COMPACT_FILTERS": (1 << 6),
    "NODE_NETWORK_LIMITED": (1 << 10),
}

def create_version(int_version, host_port, agent, start_height=0):
    host, port = host_port

    try:
        import network
        wlan = network.WLAN(network.STA_IF)
        local_ip = wlan.ifconfig()[0]
    except:
        local_ip = "0.0.0.0"

    VERSION = (int_version).to_bytes(4, "little")
    SERVICE = (0).to_bytes(8, "little")
    EPOCH = (int(time())).to_bytes(8, "little")
    RECV_ADDR = ip2b(host)
    RECV_PORT = (port).to_bytes(2, "big")
    NODE_ADDR = ip2b(local_ip)
    NODE_PORT = (8333).to_bytes(2, "big")

    nonce_high = int(time() * 1000) & 0xFFFFFFFF
    nonce_low = random.getrandbits(32)
    nonce = (nonce_high << 32) | nonce_low
    NONCE = nonce.to_bytes(8, "little")

    LENGTH_USERAGENT = (len(agent)).to_bytes(1, "little")
    USERAGENT = agent.encode()
    START_HEIGHT = (start_height).to_bytes(4, "little")

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
    timestamp = int.from_bytes(s[12:20], "little")

    recv_services = int.from_bytes(s[20:28], "little")
    recv_ip = b2ip(s[28:44])
    recv_port = int.from_bytes(s[44:46], "big")

    from_services = int.from_bytes(s[46:54], "little")
    from_ip = b2ip(s[54:70])
    from_port = int.from_bytes(s[70:72], "big")

    nonce = int.from_bytes(s[72:80], "little")

    len_agent = s[80]
    agent = s[81:81+len_agent].decode()

    start_height = int.from_bytes(s[81+len_agent:85+len_agent], "little")

    relay = None
    if len(s) > 85 + len_agent:
        relay = bool(s[85+len_agent])

    node_services = []
    for tag in SERVICES:
        if SERVICES[tag] & services > 0:
            node_services.append(tag)

    return {
        "version": version,
        "services": services,
        "services_list": node_services,
        "timestamp": timestamp,
        "addr_recv": {
            "services": recv_services,
            "ip": recv_ip,
            "port": recv_port
        },
        "addr_from": {
            "services": from_services,
            "ip": from_ip,
            "port": from_port
        },
        "nonce": nonce,
        "user_agent": agent,
        "start_height": start_height,
        "relay": relay
    }
