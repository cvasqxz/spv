import socket
from spv.peer import Peer
from spv.utils.byte import decode_sockaddr
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


def main():
    nodes = []

    for domain in DNS:
        try:
            new_nodes = socket.getaddrinfo(domain, PORT)
            print(f"DNS: {domain.upper():<32} {len(new_nodes)} IP found")
            nodes += new_nodes
        except Exception as e:
            print(f"{e}")

    tcp_nodes = [n for n in nodes if n[0] == socket.AF_INET and n[1] == socket.SOCK_STREAM]

    if not tcp_nodes:
        print("No IPs found")
        return

    node = choice(tcp_nodes)
    family, kind, proto, _, sockaddr = node
    host, port = decode_sockaddr(sockaddr)

    print(f"connecting to {host}:{port}")
    peer = Peer(MAGIC, sockaddr)

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
