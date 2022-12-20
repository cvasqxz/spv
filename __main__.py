from socket import getaddrinfo, AF_INET, SOCK_STREAM, socket
from configparser import RawConfigParser, NoSectionError
from argparse import ArgumentParser
from threading import Thread
from random import randint
from time import sleep

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

    connected = 0

    while True:
        while connected < 1:
            log_print("main", "starting connection process")
            try:
                # SELECT RANDOM NODE
                random_node = seeds[randint(0, len(seeds) - 1)]
                hostport = random_node[-1]

                # CONNECT SOCKET
                sock = socket(AF_INET, SOCK_STREAM)
                sock.settimeout(60)
                sock.connect(hostport)
                log_print("socket", "connecting to %s:%s" % hostport)

                # START THREAD
                t = Thread(
                    target=start_conn,
                    args=(
                        MAGIC,
                        hostport,
                        sock,
                    ),
                )
                t.start()

                log_print("main", "connection successfully")
                connected += 1

            except Exception as e:
                log_print("error", e)

        if t.is_alive():
            log_print("main", "Active nodes: %s" % connected)
        else:
            connected = 0

        sleep(5)


if __name__ == "__main__":
    config = RawConfigParser()
    config.read_file(open("config.ini"))

    parser = ArgumentParser(description="multichain transaction snipper")
    parser.add_argument("--network", default="bitcoin")
    args = parser.parse_args()

    main(config, args.network)
