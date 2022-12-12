from utils.byte import varint, b2ip
from time import strftime, localtime
from binascii import hexlify


def parse_addr(s):
    addresses, bytes_read = varint(s)

    addr_array = []

    for i in range(addresses):
        address = s[bytes_read + 30 * i : bytes_read + 30 * (i + 1)]

        epoch = int.from_bytes(address[0:4], "little")
        date = strftime("%d/%m/%Y %H:%M:%S", localtime(epoch))
        service = int.from_bytes(address[4:12], "little")

        ip = b2ip(address[12:28])
        port = int(hexlify(address[28:30]), 16)

        addr_array.append((ip, port))

        return addr_array
