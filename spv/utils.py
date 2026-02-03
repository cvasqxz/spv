from hashlib import sha256


def reverse_bytes(b):
    return bytes(reversed(b))


def to_hex(data):
    result = data.hex()
    # MicroPython bug: empty bytes .hex() returns bytes instead of string
    if isinstance(result, bytes):
        return result.decode()
    return result


def decode_sockaddr(addr):
    """Decode socket address from MicroPython bytearray format"""
    if isinstance(addr, (tuple, list)) and isinstance(addr[0], str):
        # Standard Python format: ('127.0.0.1', 8333)
        return addr[0], addr[1]
    elif isinstance(addr, (bytearray, bytes)):
        # MicroPython format: bytearray with packed address
        # Bytes 2-3: port (big-endian)
        # Bytes 4-7: IPv4 address
        port = int.from_bytes(addr[2:4], "big")
        ip = ".".join(str(b) for b in addr[4:8])
        return ip, port
    else:
        # Fallback: try direct unpacking
        return addr[0], addr[1]


def b2ip(s):
    ipv = s.strip(b"\x00")
    ip = ".".join([str(n) for n in ipv[-4:]])
    return ip


def ip2b(s):
    ip_s = s.split(".")

    ip_i = 0
    for i in range(len(ip_s)):
        ip_i += int(ip_s[i]) * 2 ** (24 - 8 * i)

    ip_i = 0xFFFF00000000 + ip_i

    return (ip_i).to_bytes(16, "big")


def parse_varint(s):
    if s[0] < 0xFD:
        return s[0], 1

    if s[0] == 0xFD:
        return int.from_bytes(s[1:3], "little"), 3

    if s[0] == 0xFE:
        return int.from_bytes(s[1:5], "little"), 5

    if s[0] == 0xFF:
        return int.from_bytes(s[1:9], "little"), 9


def create_varint(i):
    if i < 0xFD:
        return i.to_bytes(1, "little")

    if i >= 0xFD and i <= 0xFFFF:
        return b"\xFD" + i.to_bytes(2, "little")

    if i > 0xFFFF and i <= 0xFFFFFFFF:
        return b"\xFE" + i.to_bytes(4, "little")

    if i > 0xFFFFFFFF:
        return b"\xFF" + i.to_bytes(8, "little")


def _is_valid_command(command_bytes):
    # Find actual command length (strip trailing nulls)
    cmd_len = 12
    while cmd_len > 0 and command_bytes[cmd_len - 1] == 0:
        cmd_len -= 1

    if cmd_len == 0:
        return False

    # Check all non-null bytes are printable ASCII (32-126)
    for i in range(cmd_len):
        if command_bytes[i] < 32 or command_bytes[i] > 126:
            return False

    return True


def extract_next_message(buffer, magic, offset=0, max_payload_size=51200):
    magic_pos = buffer.find(magic, offset)

    while magic_pos != -1:
        header_start = magic_pos + len(magic)

        # Check if we have a complete header (20 bytes)
        if header_start + 20 > len(buffer):
            return None, magic_pos

        # Validate command field (12 bytes, ASCII, null-padded)
        command_bytes = buffer[header_start:header_start + 12]
        if not _is_valid_command(command_bytes):
            magic_pos = buffer.find(magic, magic_pos + 1)
            continue

        # Read and validate payload length
        payload_length = int.from_bytes(buffer[header_start + 12:header_start + 16], "little")
        if payload_length > 10_000_000:  # Sanity check
            magic_pos = buffer.find(magic, magic_pos + 1)
            continue

        # Check if we have the complete payload
        message_end = header_start + 20 + payload_length
        if message_end > len(buffer):
            return None, magic_pos

        # Verify checksum
        checksum_expected = buffer[header_start + 16:header_start + 20]
        payload_data = buffer[header_start + 20:message_end]
        checksum_actual = double256(payload_data)[:4]

        if checksum_expected != checksum_actual:
            magic_pos = buffer.find(magic, magic_pos + 1)
            continue

        # Skip messages that exceed max payload size
        if payload_length > max_payload_size:
            print(f"WARNING: Skipping large message ({payload_length} bytes)")
            return None, message_end

        # Extract and return the complete message (header + payload)
        message = buffer[header_start:message_end]
        return message, message_end

    # No magic found in remaining buffer
    return None, offset


def double256(s):
    return sha256(sha256(s).digest()).digest()
