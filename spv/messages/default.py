def pong(s):
    return s


def verack():
    return b""


def wtxidrelay():
    # BIP 339: wtxidrelay message has no payload
    return b""


def sendaddrv2():
    # BIP 155: sendaddrv2 message has no payload
    return b""


def parse_feefilter(s):
    return int.from_bytes(s[:8], "little")


def create_feefilter(i):
    return (i).to_bytes(8, "little")


def parse_sendcmpct(s):
    announce = bool(s[0])  # 1 byte: enable/disable compact blocks
    version = int.from_bytes(s[1:9], "little")  # 8 bytes: version number

    return announce, version
