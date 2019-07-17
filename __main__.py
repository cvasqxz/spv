import socket
from time import time
from random import randint
from utils.hash import double256
from utils.message import create_header, version, inv, verify_header, \
    pong, verack
from utils.log import log_print
from binascii import b2a_hex, a2b_hex

# HOST = '104.236.244.223'
# PORT = 21663
# MAGIC = 'aaa226a9'

MAGIC = 'f9beb4d9'
HOST = '72.50.221.9'
PORT = 8333

agent = '/waleta:0.1/'.encode()

buffer = b''

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    msg = version(70015, HOST, PORT, agent)
    header = create_header(msg, 'version')
    s.send(a2b_hex(MAGIC + header + msg))

    log_print('send', 'version')

    while True:

        data = buffer + s.recv(1024)
        buffer_pointer = data.rfind(a2b_hex(MAGIC))

        buffer = data[buffer_pointer:]
        data_split = data[:buffer_pointer].split(a2b_hex(MAGIC))

        for response in data_split:

            response_type = ''
            message_type = ''

            if len(response) == 0:
                continue

            # VERIFY RESPONSE
            if verify_header(response):
                response_type = response[:12].strip(b'\x00').decode()
                log_print('recv', response_type)
            else:
                continue

            # PARSE RESPONSE

            if response_type == 'inv':
                inv(response)
                message = b2a_hex(response[20:]).decode()
                message_type = 'getdata'

            if response_type == 'tx':
                log_print('new tx', b2a_hex(response).decode())

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
