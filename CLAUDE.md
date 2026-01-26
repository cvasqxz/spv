# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Bitcoin SPV (Simplified Payment Verification) client implementation in Python. It implements the Bitcoin P2P protocol to connect to Bitcoin nodes, exchange messages, and parse blockchain data.

## Running the Application

```bash
python __main__.py
```

The application connects to a random Bitcoin node from DNS seeds and establishes a P2P connection.

## Architecture

### Message-Oriented Protocol Design

The codebase follows the Bitcoin P2P protocol specification, with a clear separation between:

1. **Message creation/parsing** (`spv/messages/`)
2. **Protocol coordination** (`spv/node.py`)
3. **Low-level utilities** (`spv/utils/`)

### Protocol Flow (spv/node.py)

The `start_conn()` function implements the Bitcoin handshake and message loop:

1. **Handshake**: Send `version` message, wait for peer's `version`, exchange `verack`
2. **Message Loop**: Continuously receive data, buffer incomplete messages, parse complete messages using MAGIC bytes (`\xf9\xbe\xb4\xd9`) as delimiters
3. **Response Handling**: Parse message headers, verify checksums, dispatch to type-specific parsers
4. **Buffered Sending**: Messages are queued in `msg_buffer` and sent after processing responses

### Message Structure

All Bitcoin P2P messages follow this format (assembled in `spv/messages/header.py`):

```
MAGIC (4 bytes) + HEADER (24 bytes) + PAYLOAD (variable)
```

**Header components** (created by `create_header()`):
- Command name (12 bytes, null-padded)
- Payload length (4 bytes, little-endian)
- Checksum (4 bytes, first 4 bytes of double SHA-256)

The `verify_header()` function validates both length and checksum before processing.

### Message Types

#### version (spv/messages/version.py)
- **create_version()**: Constructs version handshake with service flags, timestamp, addresses, user agent
- **parse_version()**: Extracts peer version, services (NODE_NETWORK, NODE_WITNESS, etc.), and user agent
- Service flags are defined in the `SERVICES` dict and combined with bitwise OR

#### Transaction Processing (spv/messages/tx.py)
- **extract_tx()**: Parses both legacy and SegWit transactions
- **SegWit Detection**: Checks for `\x00\x01` flag at tx[4:6]
- **txid Calculation**: For SegWit, strips witness data before hashing (line 99-100)
- Returns JSON structure with inputs (UTXO refs, scriptsig), outputs (amount, scriptpubkey), witnesses

#### addr (spv/messages/addr.py)
- **parse_addr()**: Parses peer address announcements
- Each address: timestamp, services, IP (IPv6-mapped IPv4), port

#### inv (spv/messages/inv.py)
- **parse_inv()**: Parses inventory vectors (tx/block announcements)
- **create_invs()**: Constructs inv messages, applies witness flag (bit 30) per BIP-144

#### Simple Messages (spv/messages/default.py)
- **pong()**: Echo back ping nonce
- **verack()**: Empty message
- **feefilter**: Minimum fee rate (satoshis/kB)

### Utilities

#### spv/utils/byte.py
- **parse_varint()**: Decodes Bitcoin CompactSize integers (1, 3, 5, or 9 bytes based on prefix)
- **create_varint()**: Encodes integers to CompactSize format
- **ip2b()** / **b2ip()**: Convert between IPv4 strings and IPv6-mapped 16-byte format

#### spv/utils/hash.py
- **double256()**: Bitcoin's double SHA-256 used for checksums and transaction IDs

## Key Implementation Details

### Buffer Management (spv/node.py:24-31)
The message loop uses a sophisticated buffering strategy:
- `rfind(MAGIC)` locates the last MAGIC byte sequence
- Data before last MAGIC is processed (split by MAGIC)
- Data from last MAGIC onward is buffered for next iteration
- This handles partial messages arriving across multiple socket reads

### SegWit Transaction Parsing (spv/messages/tx.py:19-100)
Critical details:
- Flag check at line 19: `tx[4:6] == b"\x00\x01"`
- Witnesses are parsed AFTER outputs (line 76-93)
- txid excludes witness data: `tx[0:4] + tx[6:(vsize-4)] + tx[-4:]` (line 99)
- Each input can have multiple witness programs (e.g., signature + pubkey for P2WPKH)

### Service Flag Handling (spv/messages/version.py:5-17)
Service capabilities are bitwise flags:
- NODE_NETWORK (bit 0): Full node with complete blockchain
- NODE_WITNESS (bit 3): SegWit support
- NODE_NETWORK_LIMITED (bit 10): Pruned node with recent blocks
- Combine with `|=` operator when creating version message

## References

The implementation follows these specifications:
- [Bitcoin Protocol Documentation](https://en.bitcoin.it/wiki/Protocol_documentation)
- [Bitcoin P2P Network Guide](https://developer.bitcoin.org/devguide/p2p_network.html)
