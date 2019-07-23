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


def start_conn(MAGIC, HOSTPORT):
    global mempool

    start_time = time()

    # CONNECT SOCKET
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(HOSTPORT)
    log_print('socket', 'connecting to %s:%s' % HOSTPORT)

    agent = '/cvxz-spv:0.1/'

    # SEND VERSION MESSAGE
    msg = create_version(70015, HOSTPORT, agent)
    header = create_header(msg, 'version')
    sock.send(a2b_hex(MAGIC + header + msg))
    log_print('send', 'version message (%s)' % agent)

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
            else:
                continue

            # ACTIONS

            if response_type == 'inv':
                invs, message = parse_inv(response)
                log_print('recv', '%i inventory messages' % len(invs))
                log_print('invs', invs)
                message_type = 'getdata'

            elif response_type == 'tx':
                txid, tx = extract_tx(response)
                log_print('recv', 'new transaction (%s)' % txid)

                if txid not in mempool:
                    mempool.append(txid)
                    tx_json = parse_tx(tx)
                    log_print("tx json", tx_json)
                    
                    network_tps = tps(mempool, start_time)
                    log_print("network tps", network_tps)
                else:
                    continue

            elif response_type == 'addr':
                addresses = parse_addr(response)
                log_print('recv', '%i addresses' % len(addresses))
                log_print('addr', addresses)

            elif response_type == 'version':
                agent, _, version = parse_version(response)
                log_print('recv', 'version (%s, %i)' % (agent, version))

                message_type = 'verack'
                log_print('recv', 'verack')
                message = verack()

            elif response_type == 'ping':
                log_print('recv', 'ping')
                message_type = 'pong'
                message = pong(response)

            elif response_type == 'sendcmpct':
                use_cmpct, cmpct_num = parse_sendcmpct(response)

                if use_cmpct and cmpct_num == 1:
                    log_print("recv", 'sendcmpct (use cmpctblock message)')
                elif cmpct_num == 2:
                    log_print("recv", "sendcmpct (segwit active)")
                else:
                    log_print("recv", "sendcmpct (use inv/header messages)")

            elif response_type == 'feefilter':
                minfee = parse_feefilter(response)
                log_print('recv', 'feefilter (%.8f BTC)' % (minfee/1e8))

            # SEND MESSAGE
            if len(message_type) > 0:
                header = create_header(message, message_type)
                sock.send(a2b_hex(MAGIC + header + message))
                log_print('send', message_type)

    sock.close()
