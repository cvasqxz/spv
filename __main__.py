from spv.peer import Peer
from spv.utils.byte import decode_sockaddr
from net.utils.nslookup import dns_query

import socket
import random

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


def main():
    nodes_found = []

    for domain in DNS:
        new_nodes = dns_query(domain)
        print(f"DNS: {domain.upper():<32} {len(new_nodes)} IP found")
        nodes_found += new_nodes

    random_ip = random.choice(nodes_found)
    node = socket.getaddrinfo(random_ip, 8333, socket.AF_INET, socket.SOCK_STREAM)
    family, kind, proto, _, sockaddr = node[0]
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
