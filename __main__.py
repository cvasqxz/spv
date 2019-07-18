import socket
from time import time
from random import randint
from utils.hash import double256
from messages.tx import parse_tx
from messages.header import create_header, verify_header
from messages.default import pong, verack
from messages.version import create_version, parse_version
from messages.sendcmpct import parse_sendcmpct
from messages.inv import parse_inv
from utils.log import log_print
from binascii import b2a_hex, a2b_hex

from configparser import RawConfigParser

agent = '/waleta:0.1/'.encode()

def main(config, network='bitcoin'):

    DNS = config.get(network, 'DNS')
    MAGIC = config.get(network, 'MAGIC')
    PORT = config.get(network, 'PORT')

    # DNS LOOKUP
    seeds = socket.getaddrinfo(DNS, PORT, socket.AF_INET, socket.SOCK_STREAM)
    log_print('dns', 'request nodes to %s (%i found)' % (DNS, len(seeds)))

    # SELECT RANDOM NODE
    random_node = seeds[randint(0, len(seeds) - 1)]
    node_hostport = random_node[4]
    
    # CONNECT SOCKET
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(node_hostport)
    log_print('socket', 'connecting to %s:%s' % random_node[4])

    # SEND VERSION MESSAGE
    msg = create_version(70015, node_hostport, agent)
    header = create_header(msg, 'version')
    s.send(a2b_hex(MAGIC + header + msg))
    log_print('send', 'version')

    buffer = b''

    while True:

        # SOCKET BUFFER
        data = buffer + s.recv(1024)
        buffer_pointer = data.rfind(a2b_hex(MAGIC))

        buffer = data[buffer_pointer:]
        data_split = data[:buffer_pointer].split(a2b_hex(MAGIC))

        # RESPONSE PARSER
        for response in data_split:

            response_type = ''
            message_type = ''

            # VERIFY RESPONSE
            if len(response) == 0:
                continue

            if verify_header(response):
                response_type = response[:12].strip(b'\x00').decode()
                log_print('recv', response_type)
            else:
                continue

            # ACTIONS



            if response_type == 'inv':
                message = parse_inv(response)
                message_type = 'getdata'

            elif response_type == 'tx':
                parse_tx(response)

            elif response_type == 'version':
                parse_version(response)
                message_type = 'verack'
                message = verack()

            elif response_type == 'ping':
                message_type = 'pong'
                message = pong(response)

            elif response_type == 'sendcmpct':
                parse_sendcmpct(response)

            # SEND MESSAGE
            if len(message_type) > 0:
                header = create_header(message, message_type)
                s.send(a2b_hex(MAGIC + header + message))
                log_print('send', message_type)

    s.close()

if __name__ == "__main__":

    config = RawConfigParser()
    config.read_file(open('config.ini'))

    main(config)
