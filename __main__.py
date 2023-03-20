from socket import getaddrinfo, AF_INET, SOCK_STREAM, socket
from configparser import RawConfigParser, NoSectionError
from argparse import ArgumentParser
from threading import Thread
from binascii import unhexlify
from random import choice

from spv.node import start_conn
from spv.utils.log import log_print


def main(config, network):
    try:
        DNS = config.get(network, "DNS")
        MAGIC = config.get(network, "MAGIC")
        PORT = config.get(network, "PORT")
    except NoSectionError:
        log_print("error", "Network %s not found" % network)
        exit()

    # DNS LOOKUP
    seeds = getaddrinfo(DNS, PORT, AF_INET, SOCK_STREAM)
    log_print("dns", "request nodes to %s (%i found)" % (DNS, len(seeds)))

    try:
        log_print("main", "starting connection process")
        
        # SELECT RANDOM NODE
        random_node = choice(seeds)[-1]

        # CONNECT SOCKET
        log_print("main", "connecting to %s:%s" % random_node)
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(30)
        sock.connect(random_node)

        # START THREAD
        thread_args = (unhexlify(MAGIC), random_node, sock)
        t = Thread(target=start_conn, args=thread_args,)
        t.start()

        log_print("main", "connection successfully")

    except Exception as e:
        log_print("error", e)


if __name__ == "__main__":
    config = RawConfigParser()
    config.read_file(open("config.ini"))

    parser = ArgumentParser(description="multichain transaction snipper")
    parser.add_argument("--network", default="bitcoin")
    args = parser.parse_args()

    main(config, args.network)
