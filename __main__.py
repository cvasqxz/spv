from configparser import RawConfigParser
import threading
from utils.log import log_print
from random import randint
from node import start_conn

from socket import getaddrinfo, AF_INET, SOCK_STREAM

def main(config, network='bitcoin'):
    DNS = config.get(network, 'DNS')
    MAGIC = config.get(network, 'MAGIC')
    PORT = config.get(network, 'PORT')

    # DNS LOOKUP
    seeds = getaddrinfo(DNS, PORT, AF_INET, SOCK_STREAM)
    log_print('dns', 'request nodes to %s (%i found)' % (DNS, len(seeds)))

    # SELECT RANDOM NODE
    random_node = seeds[randint(0, len(seeds) - 1)]
    hostport = random_node[4]

    t = threading.Thread(target=start_conn, args=(MAGIC, hostport, ))
    t.start()

if __name__ == "__main__":

    config = RawConfigParser()
    config.read_file(open('config.ini'))

    main(config)
