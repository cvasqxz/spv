from messages.default import pong, verack, parse_sendcmpct, parse_feefilter
from messages.version import create_version, parse_version
from messages.header import create_header, verify_header
from messages.addr import parse_addr
from messages.tx import extract_tx
from messages.inv import parse_inv

from utils.log import log_print

from binascii import hexlify, unhexlify


def start_conn(MAGIC, HOSTPORT, sock):
    global mempool, network_tps

    client_agent = "/cvxz-spv:0.2/"
    client_version = 70016

    MAGIC = unhexlify(MAGIC)

    # SEND VERSION MESSAGE
    msg = create_version(client_version, HOSTPORT, client_agent)
    header = create_header(msg, "version")
    sock.send(MAGIC + header + msg)

    log_print("send", "version (%s, %i)" % (client_agent, client_version))

    buffer = b""

    while True:
        # SOCKET BUFFER
        data = buffer + sock.recv(1024)
        buffer_pointer = data.rfind(MAGIC)

        buffer = data[buffer_pointer:]
        data_split = data[:buffer_pointer].split(MAGIC)

        # RESPONSE PARSER
        for response in data_split:
            response_type = ""
            message_type = ""

            if len(response) > 0 and verify_header(response):
                response_type = bytes.decode(response[:12].strip(b"\x00"))
            else:
                continue

            # REMOVE HEADER
            response = response[20:]

            # ACTIONS
            if response_type == "inv":
                invs, message = parse_inv(response)
                message_type = "getdata"

                log_print("recv %s:%s" % HOSTPORT, "%i inventory messages" % len(invs))

                for inv in invs:
                    log_print("inv", "%s: %s" % (inv["type"], hexlify(inv["content"])))

            if response_type == "tx":
                txid, tx = extract_tx(response)
                log_print(
                    "recv %s:%s" % HOSTPORT,
                    "new tx (%s): %s" % (hexlify(txid), hexlify(tx)),
                )

            if response_type == "addr":
                addrs = parse_addr(response)
                log_print("recv %s:%s" % HOSTPORT, "addresses: %s" % addrs)

            if response_type == "version":
                agent, service, version = parse_version(response)
                message_type = "verack"
                message = verack()
                log_print(
                    "recv %s:%s" % HOSTPORT,
                    "version (%s, %i, %s)" % (agent, version, service),
                )

            if response_type == "ping":
                message_type = "pong"
                message = pong(response)
                log_print("recv %s:%s" % HOSTPORT, "ping")

            if response_type == "sendcmpct":
                usecmpct, cmpctnum = parse_sendcmpct(response)
                log_print(
                    "recv %s:%s" % HOSTPORT, "sendcmpct (%s, %i)" % (usecmpct, cmpctnum)
                )

            if response_type == "feefilter":
                minfee = parse_feefilter(response)
                log_print(
                    "recv %s:%s" % HOSTPORT, "feefilter (%.8f BTC)" % (minfee / 1e8)
                )

            # SEND MESSAGE
            if len(message_type) > 0:
                header = create_header(message, message_type)
                sock.send(MAGIC + header + message)
                log_print("send %s:%s" % HOSTPORT, message_type)

    sock.close()
