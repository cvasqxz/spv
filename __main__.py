import socket
from spv.peer import Peer
from random import choice

DNS = [
    "seed.bitcoin.wiz.biz",
    "dnsseed.bluematt.me",
    "seed.bitcoinstats.com",
    "seed.btc.petertodd.net",
    "seed.bitcoin.sprovoost.nl",
    "dnsseed.emzy.de",
    "seed.bitcoin.wiz.biz"
]
MAGIC = b'\xf9\xbe\xb4\xd9'
PORT = 8333


def decode_sockaddr(addr):
    """Decode socket address from MicroPython bytearray format"""
    if isinstance(addr, (tuple, list)) and isinstance(addr[0], str):
        # Standard Python format: ('127.0.0.1', 8333)
        return addr[0], addr[1]
    elif isinstance(addr, (bytearray, bytes)):
        # MicroPython format: bytearray with packed address
        # Bytes 2-3: port (big-endian)
        # Bytes 4-7: IPv4 address
        port = int.from_bytes(addr[2:4], "big")
        ip = ".".join(str(b) for b in addr[4:8])
        return ip, port
    else:
        # Fallback: try direct unpacking
        return addr[0], addr[1]

def main():
    nodes = []

    for domain in DNS:
        try:
            new_nodes = socket.getaddrinfo(domain, PORT)
            print(f"DNS: {domain.upper():<32} {len(new_nodes)} IP found")
            nodes += new_nodes
        except Exception as e:
            print(f"{e}")

    tcp_nodes = [n for n in nodes if n[1] == socket.SOCK_STREAM]

    if not tcp_nodes:
        print("No IPs found")
        return

    node = choice(tcp_nodes)
    family, kind, proto, _, addr = node
    host, port = decode_sockaddr(addr)

    print(f"connecting to {host}:{port}")
    peer = Peer(MAGIC, host, port)

    try:
        peer.connect()
        print("connection successfully")
        peer.handshake()
        peer.run()
    except Exception as e:
        print(f"error {e}")
        peer.close()


if __name__ == "__main__":
    main()
