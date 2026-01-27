import socket
from spv.messages.default import pong, verack, parse_sendcmpct, parse_feefilter, create_feefilter
from spv.messages.version import create_version, parse_version
from spv.messages.header import create_header, verify_header
from spv.messages.addr import parse_addr
from spv.messages.inv import parse_inv
from spv.utils.byte import decode_sockaddr


class Peer:
    def __init__(self, magic, sockaddr, client_agent="/cvasqxz_spv:0.1.0/", version=70016):
        self.magic = magic
        self.sockaddr = sockaddr  # Native socket address for connect()
        self.client_agent = client_agent
        self.version = version
        self.sock = None

        self.buffer = b""
        self.response_array = []

    def is_connected(self):
        return self.sock is not None and self.sock.fileno() != -1

    def connect(self, timeout=60):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.sock.connect(self.sockaddr)

    def handshake(self):
        host, port = decode_sockaddr(self.sockaddr)
        version_message = create_version(self.version, (host, port), self.client_agent)
        header = create_header("version", version_message)
        # MicroPython requires bytearray for socket.send()
        message = bytearray(self.magic + header + version_message)
        self.sock.send(message)
        print(f"send version ({self.client_agent}, {self.version})")

        self.response_array.append({"type": "feefilter", "content": create_feefilter(1000)})

    def send_message(self, msg_type, msg_content):
        header = create_header(msg_type, msg_content)
        message = bytearray(self.magic + header + msg_content)
        self.sock.send(message)
        print(f"SEND {msg_type}")

    def _process_messages(self):
        data = self.buffer
        buffer_pointer = data.rfind(self.magic)

        if buffer_pointer == -1:
            self.buffer = data
            data_split = []
        else:
            self.buffer = data[buffer_pointer:]
            data_split = data[:buffer_pointer].split(self.magic)

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
                self.response_array.append({"type": "verack", "content": verack()})
                print(f"\tversion ({agent}, {version}, {service})")

            if response_type == "ping":
                self.response_array.append({"type": "pong", "content": pong(response)})

            if response_type == "sendcmpct":
                usecmpct, cmpctnum = parse_sendcmpct(response)
                print(f"\tsendcmpct ({usecmpct}, {cmpctnum})")

            if response_type == "feefilter":
                minfee = parse_feefilter(response)
                print(f"\tfeefilter ({minfee} satoshis)")

            if response_type == "inv":
                invs = parse_inv(response)
                print(f"\tinv ({len(invs)} headers)")
                self.response_array.append({"type": "getdata", "content": response})

    def _send_pending_messages(self):
        while self.response_array:
            response = self.response_array.pop(0)
            response_type = response["type"]
            response_content = response["content"]
            header = create_header(response_type, response_content)

            message = bytearray(self.magic + header + response_content)
            self.sock.send(message)
            print(f"SEND {response_type}")

    def run(self):
        while self.is_connected:
            try:
                # SOCKET BUFFER
                packet_recv = self.sock.recv(1024)

                if not packet_recv:
                    print("Connection closed by peer")
                    break

                self.buffer += packet_recv

                # Process received messages
                self._process_messages()

                # Send pending messages
                self._send_pending_messages()

            except Exception as e:
                print(f"Error in run loop: {e}")
                break

        self.close()

    def close(self):
        if self.is_connected():
            self.sock.close()
            print("Connection closed")
