from socket import getaddrinfo, AF_INET, SOCK_STREAM
from configparser import RawConfigParser
from utils.log import log_print
from threading import Thread
from node import start_conn
from random import randint
from time import time


def main(config, network='bitcoin'):

    nodes = []

    DNS = config.get(network, 'DNS')
    MAGIC = config.get(network, 'MAGIC')
    PORT = config.get(network, 'PORT')

    # DNS LOOKUP
    seeds = getaddrinfo(DNS, PORT, AF_INET, SOCK_STREAM)
    log_print('dns', 'request nodes to %s (%i found)' % (DNS, len(seeds)))

    start_time = time()

    while len(nodes) < 8:
        # SELECT RANDOM NODE
        random_node = seeds[randint(0, len(seeds) - 1)]
        hostport = random_node[4]

        if hostport not in nodes:
            nodes.append(hostport)
            log_print("threading", "starting node %i" % len(nodes))
            t = Thread(target=start_conn, args=(MAGIC, hostport, start_time, ))
            t.start()


if __name__ == "__main__":

    config = RawConfigParser()
    config.read_file(open('config.ini'))

    main(config)
