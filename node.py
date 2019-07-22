from messages.version import create_version, parse_version
from messages.header import create_header, verify_header
from messages.feefilter import parse_feefilter
from messages.sendcmpct import parse_sendcmpct
from messages.default import pong, verack
from messages.addr import parse_addr
from messages.inv import parse_inv
from messages.tx import extract_tx, parse_tx, tps
from utils.log import log_print

from socket import socket, AF_INET, SOCK_STREAM
from binascii import a2b_hex
from time import time

mempool = []

def start_conn(MAGIC, HOSTPORT, START_TIME):
    global mempool

    # CONNECT SOCKET
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(HOSTPORT)
    log_print('socket', 'connecting to %s:%s' % HOSTPORT)

    agent = '/cvxz-spv:0.1/'.encode()

    # SEND VERSION MESSAGE
    msg = create_version(70015, HOSTPORT, agent)
    header = create_header(msg, 'version')
    sock.send(a2b_hex(MAGIC + header + msg))
    log_print('send', 'version')

    buffer = b''

    while True:

        # SOCKET BUFFER
        data = buffer + sock.recv(1024)
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
                txid, tx = extract_tx(response)

                if txid not in mempool:
                    mempool.append(txid)
                    tx_dict = parse_tx(tx)
                    log_print("tx", tx_dict)
                    print("Added to MemPool (%i transactions)" % len(mempool))
                    network_tps = tps(mempool, START_TIME)
                    log_print("network tps", network_tps)

            elif response_type == 'addr':
                parse_addr(response)

            elif response_type == 'version':
                parse_version(response)
                message_type = 'verack'
                message = verack()

            elif response_type == 'ping':
                message_type = 'pong'
                message = pong(response)

            elif response_type == 'sendcmpct':
                parse_sendcmpct(response)

            elif response_type == 'feefilter':
                parse_feefilter(response)

            # SEND MESSAGE
            if len(message_type) > 0:
                header = create_header(message, message_type)
                sock.send(a2b_hex(MAGIC + header + message))
                log_print('send', message_type)

    sock.close()
