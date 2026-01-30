import socket
import gc
from spv.messages.default import pong, verack, wtxidrelay, sendaddrv2, parse_sendcmpct, parse_feefilter, create_feefilter
from spv.messages.version import create_version, parse_version
from spv.messages.header import create_header, verify_header
from spv.messages.addr import parse_addr, parse_addrv2
from spv.messages.inv import parse_inv, create_getdata
from spv.messages.tx import parse_tx
from spv.utils.byte import decode_sockaddr, extract_next_message


class Peer:
    def __init__(self, magic, sockaddr, client_agent="/cvasqxz_spv:0.1.0/", version=70016):
        self.magic = magic
        self.sockaddr = sockaddr  # Native socket address for connect()
        self.client_agent = client_agent
        self.version = version
        self.sock = None

        # Handshake state
        self.version_received = False
        self.verack_received = False
        self.handshake_completed = False

        self.buffer = b""
        self.response_array = []

        # Enable garbage collection and set threshold
        gc.enable()
        gc.threshold(4096)

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

    def _check_handshake_complete(self):
        if self.version_received and self.verack_received and not self.handshake_completed:
            self.handshake_completed = True
            print("Handshake complete")
            # Queue messages that should only be sent after handshake
            self.response_array.append({"type": "getaddr", "content": b""})
            self.response_array.append({"type": "feefilter", "content": create_feefilter(1000)})

    def send_message(self, msg_type, msg_content):
        header = create_header(msg_type, msg_content)
        message = bytearray(self.magic + header + msg_content)
        self.sock.send(message)
        print(f"SEND {msg_type}")

    def _process_messages(self):
        offset = 0

        while True:
            message, message_end, preserve_from = extract_next_message(self.buffer, self.magic, offset)

            if message is None:
                self.buffer = self.buffer[preserve_from:]
                break

            # Verify header
            if verify_header(message):
                response_type = bytes.decode(message[:12].strip(b"\x00"))
                print(f"RECV {response_type}")

                # Extract payload (skip 20-byte header)
                payload = message[20:]

                # ACTIONS
                if response_type == "addr":
                    addrs = parse_addr(payload)
                    print(f"\taddresses {len(addrs)}")
                    del addrs

                if response_type == "addrv2":
                    addrs = parse_addrv2(payload)
                    print(f"\tv2 addresses {len(addrs)}")
                    del addrs

                if response_type == "version":
                    ver = parse_version(payload)
                    print(f"\tversion {ver}")
                    # BIP 339 & BIP 155: Send wtxidrelay and sendaddrv2 before verack
                    self.response_array.append({"type": "wtxidrelay", "content": wtxidrelay()})
                    self.response_array.append({"type": "sendaddrv2", "content": sendaddrv2()})
                    self.response_array.append({"type": "verack", "content": verack()})
                    self.version_received = True
                    self._check_handshake_complete()
                    del ver

                if response_type == "verack":
                    self.verack_received = True
                    self._check_handshake_complete()

                if response_type == "ping":
                    self.response_array.append({"type": "pong", "content": pong(payload)})

                if response_type == "sendcmpct":
                    usecmpct, cmpctnum = parse_sendcmpct(payload)
                    print(f"\tsendcmpct ({usecmpct}, {cmpctnum})")
                    del usecmpct, cmpctnum

                if response_type == "feefilter":
                    minfee = parse_feefilter(payload)
                    print(f"\tfeefilter ({minfee} satoshis)")
                    del minfee

                if response_type == "inv":
                    invs = parse_inv(payload)
                    print(f"\tinv ({len(invs)} items)")

                    # Filter only transactions (ignore blocks to save memory)
                    tx_invs = [inv for inv in invs if inv["type"] in ["MSG_TX", "MSG_WITNESS_TX"]]

                    if tx_invs:
                        getdata_payload = create_getdata(tx_invs)
                        self.response_array.append({"type": "getdata", "content": getdata_payload})
                        del getdata_payload
                    
                    del invs, tx_invs

                if response_type == "tx":
                    tx = parse_tx(payload)
                    print(f"\ttransaction: {tx}")
                    del tx

            # Move offset past this message
            offset = message_end
            gc.collect()

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
        while self.is_connected():
            packet_recv = self.sock.recv(1024)

            if not packet_recv:
                print("Connection closed by peer")
                break

            self.buffer += packet_recv

            self._process_messages()
            self._send_pending_messages()

            # Trigger garbage collection to free processed messages
            gc.collect()

        self.close()

    def close(self):
        if self.is_connected():
            try:
                self.sock.close()
                print("Connection closed")
            except:
                pass
        self.sock = None
