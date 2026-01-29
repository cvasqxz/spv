from spv.utils.byte import parse_varint, b2ip, to_hex
from time import localtime


def parse_addr(s):
    addresses, bytes_read = parse_varint(s)

    addr_array = []

    for i in range(addresses):
        address = s[bytes_read + 30 * i : bytes_read + 30 * (i + 1)]

        # Validate we have a complete address (30 bytes)
        if len(address) < 30:
            break

        epoch = int.from_bytes(address[0:4], "little")
        service = int.from_bytes(address[4:12], "little")

        ip = b2ip(address[12:28])
        port = int.from_bytes(address[28:30], "big")

        addr_array.append((ip, port, epoch, service))

    return addr_array


def parse_addrv2(s):
    """Parse addrv2 message with support for multiple address types (BIP155)"""
    addresses, bytes_read = parse_varint(s)
    addr_array = []
    offset = bytes_read

    address_types = {
        0: "IPv4",
        1: "IPv6",
        2: "Tor v2",
        3: "Tor v3",
        4: "I2P",
        5: "CJDNS"
    }

    for i in range(addresses):
        # Parse timestamp (4 bytes, little-endian uint32)
        timestamp = int.from_bytes(s[offset:offset+4], "little")
        offset += 4

        # Parse services (variable-length compactSize uint)
        services, services_len = parse_varint(s[offset:])
        offset += services_len

        # Parse network id (1 byte uint8_t)
        addr_type = s[offset]
        offset += 1
        type_name = address_types.get(addr_type, f"Unknown({addr_type})")

        # Parse address length (variable-length compactSize uint)
        addr_len, addr_len_bytes = parse_varint(s[offset:])
        offset += addr_len_bytes

        # Parse address bytes
        address_bytes = s[offset:offset + addr_len]
        offset += addr_len

        # Parse port (2 bytes, big-endian uint16_t)
        port = int.from_bytes(s[offset:offset + 2], "big")
        offset += 2

        # Format address based on type
        if addr_type == 0:  # IPv4
            address_str = ".".join(str(b) for b in address_bytes)
        elif addr_type == 1:  # IPv6
            address_str = ":".join(f"{int.from_bytes(address_bytes[i:i+2], 'big'):x}" for i in range(0, 16, 2))
        else:  # Tor, I2P, CJDNS (in hex)
            address_str = to_hex(address_bytes)

        addr_array.append({
            "type": type_name,
            "address": address_str,
            "port": port,
            "timestamp": timestamp,
            "services": services
        })

    return addr_array
