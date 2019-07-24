from socket import getaddrinfo, AF_INET, SOCK_STREAM, socket
from configparser import RawConfigParser
from utils.log import log_print
from threading import Thread
from node import start_conn
from random import randint
from pulsar.apps import wsgi
from api.methods import hello

sockets = []
nodes = []


def main(config, network='bitcoin'):

    DNS = config.get(network, 'DNS')
    MAGIC = config.get(network, 'MAGIC')
    PORT = config.get(network, 'PORT')

    # DNS LOOKUP
    seeds = getaddrinfo(DNS, PORT, AF_INET, SOCK_STREAM)
    log_print('dns', 'request nodes to %s (%i found)' % (DNS, len(seeds)))

    while len(nodes) < 4:
        # SELECT RANDOM NODE
        random_node = seeds[randint(0, len(seeds) - 1)]
        hostport = random_node[4]

        if hostport not in nodes:
            nodes.append(hostport)

            # CONNECT SOCKET
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect(hostport)
            sockets.append(sock)
            log_print('socket', 'connecting to %s:%s' % hostport)
            t = Thread(target=start_conn, args=(MAGIC, hostport, sock, ))
            t.start()

    wsgi.WSGIServer(callable=hello).start()

if __name__ == "__main__":

    config = RawConfigParser()
    config.read_file(open('config.ini'))

    main(config)
