from socket import getaddrinfo, AF_INET, SOCK_STREAM, socket
from configparser import RawConfigParser
from utils.log import log_print
from threading import Thread
from node import start_conn
from random import randint
from time import sleep


def main(config, network="bitcoin"):

    DNS = config.get(network, "DNS")
    MAGIC = config.get(network, "MAGIC")
    PORT = config.get(network, "PORT")

    # DNS LOOKUP
    seeds = getaddrinfo(DNS, PORT, AF_INET, SOCK_STREAM)
    log_print("dns", "request nodes to %s (%i found)" % (DNS, len(seeds)))

    connected = False

    while True:
        while not connected:
            log_print("main", "starting connection process")
            try:
                # SELECT RANDOM NODE
                random_node = seeds[randint(0, len(seeds) - 1)]
                hostport = random_node[-1]

                # CONNECT SOCKET
                sock = socket(AF_INET, SOCK_STREAM)
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
                connected = True

            except Exception as e:
                log_print("error", e)

        if t.is_alive():
            log_print("main", "Heartbeat <3")
        else:
            connected = False

        sleep(5)


if __name__ == "__main__":

    config = RawConfigParser()
    config.read_file(open("config.ini"))

    main(config)
