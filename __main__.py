import socket
from time import time
from random import randint
from utils.hash import double256
from messages.tx import parse_tx
from messages.header import create_header, verify_header
from messages.default import pong, verack
from messages.version import create_version
from messages.inv import parse_inv
from utils.log import log_print
from binascii import b2a_hex, a2b_hex

# HOST = '104.236.244.223'
# PORT = 21663
# MAGIC = 'aaa226a9'

MAGIC = 'f9beb4d9'

agent = '/waleta:0.1/'.encode()

def main():

    # DNS LOOKUP
    dns_seeds = socket.getaddrinfo('seed.bitcoin.sipa.be', 8333, socket.AF_INET, socket.SOCK_STREAM)
    log_print('dns', '%i nodes found' % len(dns_seeds))

    # SELECT RANDOM NODE
    random_node = dns_seeds[randint(0, len(dns_seeds) - 1)]
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

            if response_type == 'tx':
                parse_tx(response)

            elif response_type == 'version':
                message_type = 'verack'
                message = verack()

            elif response_type == 'ping':
                message_type = 'pong'
                message = pong(response)

            # SEND MESSAGE
            if len(message_type) > 0:
                header = create_header(message, message_type)
                s.send(a2b_hex(MAGIC + header + message))
                log_print('send', message_type)

    s.close()

if __name__ == "__main__":
    main()