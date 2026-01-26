import socket
from spv.node import start_conn
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
        print(f"DNS: {domain.upper():<32}", end="")
        
        try:
            new_nodes = socket.getaddrinfo(domain, PORT)
            print(f"{len(new_nodes)} IP found")
            nodes += new_nodes
        except Exception as e:
            print(f"{e}")

    print(f"\nTOTAL IP FOUND: {len(nodes)}")

    # Filtrar solo sockets TCP (SOCK_STREAM)
    tcp_nodes = [n for n in nodes if n[1] == socket.SOCK_STREAM]

    if not tcp_nodes:
        print("No se encontraron nodos TCP disponibles")
        return

    connected = False
    while not connected:
        node = choice(tcp_nodes)
        try:
            print(f"connecting to {node}")
            family, kind, proto, _, addr = node

            sock = socket.socket(family, kind, proto)
            sock.settimeout(60)
            sock.connect(addr)
            connected = True

        except Exception as e:
            print(f"error {e}")

    # START THREAD
    print("connection successfully")
    start_conn(MAGIC, addr, sock)



if __name__ == "__main__":
    main()
