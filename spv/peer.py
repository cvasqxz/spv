import socket
import gc
from spv.messages.default import pong, verack, wtxidrelay, sendaddrv2, parse_sendcmpct, parse_feefilter, create_feefilter
from spv.messages.version import create_version, parse_version
from spv.messages.header import create_header, verify_header
from spv.messages.addr import parse_addr, parse_addrv2
from spv.messages.inv import parse_inv, create_getdata
from spv.messages.tx import parse_tx
from spv.utils import decode_sockaddr, extract_next_message


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
        gc.threshold(16384)  # 16 KB - balance between memory usage and GC frequency

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
        message_found = True

        while message_found:
            message, next_offset = extract_next_message(self.buffer, self.magic, offset)

            if message is None:
                # No complete message available - preserve buffer from next_offset
                self.buffer = self.buffer[next_offset:]
                message_found = False
            else:
                # Process the message (already validated by extract_next_message)
                command = bytes.decode(message[:12].strip(b"\x00"))
                payload = message[20:]  # Skip 20-byte header

                # Handle message by type
                if command == "version":
                    ver = parse_version(payload)
                    print(f"RECV version {ver['user_agent'], ver['version']}")
                    # BIP 339 & BIP 155: Send wtxidrelay and sendaddrv2 before verack
                    self.response_array.append({"type": "wtxidrelay", "content": wtxidrelay()})
                    self.response_array.append({"type": "sendaddrv2", "content": sendaddrv2()})
                    self.response_array.append({"type": "verack", "content": verack()})
                    self.version_received = True
                    self._check_handshake_complete()
                    del ver

                elif command == "verack":
                    self.verack_received = True
                    self._check_handshake_complete()

                elif command == "ping":
                    self.response_array.append({"type": "pong", "content": pong(payload)})

                elif command == "addr":
                    addrs = parse_addr(payload)
                    print(f"RECV addresses {len(addrs)}")
                    del addrs

                elif command == "addrv2":
                    addrs = parse_addrv2(payload)
                    print(f"RECV v2 addresses {len(addrs)}")
                    del addrs

                elif command == "sendcmpct":
                    usecmpct, cmpctnum = parse_sendcmpct(payload)
                    print(f"RECV sendcmpct ({usecmpct}, {cmpctnum})")
                    del usecmpct, cmpctnum

                elif command == "feefilter":
                    minfee = parse_feefilter(payload)
                    print(f"RECV feefilter ({minfee} satoshis)")
                    del minfee

                elif command == "inv":
                    invs = parse_inv(payload)
                    print(f"RECV inv ({len(invs)} items)")

                    # Filter only transactions (ignore blocks to save memory)
                    tx_invs = [inv for inv in invs if inv["type"] in ["MSG_TX", "MSG_WTX", "MSG_WITNESS_TX"]]

                    if tx_invs:
                        getdata_payload = create_getdata(tx_invs)
                        self.response_array.append({"type": "getdata", "content": getdata_payload})
                        del getdata_payload

                    del invs, tx_invs

                elif command == "tx":
                    tx = parse_tx(payload)
                    print(f"RECV tx {tx['txid']}")
                    del tx

                # Continue processing from next message
                offset = next_offset

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

            # Collect garbage once per recv cycle (not per message)
            # The gc.threshold(16384) handles automatic collection between cycles
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
