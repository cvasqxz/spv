from spv.messages.default import pong, verack, parse_sendcmpct, parse_feefilter, create_feefilter
from spv.messages.version import create_version, parse_version
from spv.messages.header import create_header, verify_header
from spv.messages.addr import parse_addr
from spv.messages.inv import parse_inv

from binascii import hexlify

def start_conn(MAGIC, HOSTPORT, sock):
    client_agent = f"/cvasqxz_spv:0.1.0/"
    client_version = 70016

    # SEND VERSION MESSAGE
    version_message = create_version(client_version, HOSTPORT, client_agent)
    header = create_header("version", version_message)
    sock.send(MAGIC + header + version_message)

    print(f"send version ({client_agent}, {client_version})")

    buffer = b""
    response_array = []

    response_array.append({"type": "feefilter", "content": create_feefilter(1000)})

    while True:
        # SOCKET BUFFER
        packet_recv = sock.recv(1024)

        if not packet_recv:
            print("Connection closed by peer")
            break

        data = buffer + packet_recv
        buffer_pointer = data.rfind(MAGIC)

        if buffer_pointer == -1:
            buffer = data
            data_split = []
        else:
            buffer = data[buffer_pointer:]
            data_split = data[:buffer_pointer].split(MAGIC)

        # RESPONSE PARSER
        for response in data_split:
            if len(response) > 0 and verify_header(response):
                response_type = bytes.decode(response[:12].strip(b"\x00"))
                print(f"RECV {response_type}")
            else:
                continue

            # REMOVE HEADER
            response = response[20:]

            # ACTIONS
            if response_type == "addr":
                addrs = parse_addr(response)
                print(f"\taddresses: {addrs}")

            if response_type == "version":
                agent, service, version = parse_version(response)
                response_array.append({"type": "verack", "content": verack()})
                print(f"\tversion ({agent}, {version}, {service})")

            if response_type == "ping":
                response_array.append({"type": "pong", "content": pong(response)})

            if response_type == "sendcmpct":
                usecmpct, cmpctnum = parse_sendcmpct(response)
                print(f"\tsendcmpct ({usecmpct}, {cmpctnum})")

            if response_type == "feefilter":
                minfee = parse_feefilter(response)
                print(f"\tfeefilter ({minfee} satoshis)")

            if response_type == "inv":
                invs = parse_inv(response)
                print(f"\tinv ({len(invs)} headers)")
                response_array.append({"type": "getdata", "content": response})

        while response_array:
            response = response_array.pop(0)
            response_type    = response["type"]
            response_content = response["content"]
            header = create_header(response_type, response_content)

            sock.send(MAGIC + header + response_content)
            print(f"SEND {response_type}")

    sock.close()
