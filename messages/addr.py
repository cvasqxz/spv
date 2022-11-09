from utils.byte import varint, b2ip, b2a
from time import strftime, localtime


def parse_addr(s):
    addresses, bytes_read = varint(s[20:])

    addr_array = []

    for i in range(addresses):
        address = s[20 + bytes_read + 30 * i : 20 + bytes_read + 30 * (i + 1)]

        epoch = int.from_bytes(address[0:4], "little")
        date = strftime("%d/%m/%Y %H:%M:%S", localtime(epoch))
        service = int.from_bytes(address[4:12], "little")

        ip = b2ip(address[12:28])
        port = int(b2a(address[28:30]), 16)

        addr_array.append((ip, port))

        return addr_array
