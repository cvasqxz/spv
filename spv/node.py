from spv.messages.default import pong, verack, parse_sendcmpct, parse_feefilter, create_feefilter
from spv.messages.version import create_version, parse_version
from spv.messages.header import create_header, verify_header
from spv.messages.tx import extract_tx, get_satoshis
from spv.messages.inv import parse_inv, create_invs
from spv.messages.addr import parse_addr
from spv.utils.log import log_print

def start_conn(MAGIC, HOSTPORT, sock):
    global mempool, network_tps

    client_agent = "/cvxz-spv:0.2/"
    client_version = 70016

    # SEND VERSION MESSAGE
    msg = create_version(client_version, HOSTPORT, client_agent)
    header = create_header(msg, "version")
    sock.send(MAGIC + header + msg)

    log_print("send", "version (%s, %i)" % (client_agent, client_version))

    buffer = b""
    msg_buffer = []

    msg_buffer.append({"message_type": "feefilter", "message": create_feefilter(1000)})

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
                invs = parse_inv(response)
                msg_buffer.append(
                    {"message_type": "getdata", "message": create_invs(invs)}
                )
                log_print("recv %s:%s" % HOSTPORT, "%i inventory messages" % len(invs))

            if response_type == "tx":
                json_tx = extract_tx(response)
                log_print(
                    "recv %s:%s" % HOSTPORT,
                    "new tx: %s (%.8f BTC)" % (json_tx["txid"], get_satoshis(json_tx)),
                )

            if response_type == "addr":
                addrs = parse_addr(response)
                log_print("recv %s:%s" % HOSTPORT, "addresses: %s" % addrs)

            if response_type == "version":
                agent, service, version = parse_version(response)
                msg_buffer.append({"message_type": "verack", "message": verack()})
                log_print(
                    "recv %s:%s" % HOSTPORT,
                    "version (%s, %i, %s)" % (agent, version, service),
                )

            if response_type == "ping":
                msg_buffer.append({"message_type": "pong", "message": pong(response)})
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
        if len(msg_buffer) == 0:
            continue

        for msg in range(len(msg_buffer)):
            response = msg_buffer.pop()
            header = create_header(response["message"], response["message_type"])
            sock.send(MAGIC + header + response["message"])
            log_print("send %s:%s" % HOSTPORT, response["message_type"])

    sock.close()
