from utils.byte import varint, hex_ip, b2a
# from utils.byte import reverse
# from utils.log import log_print
# from time import strftime, localtime


def parse_addr(s):
    addresses, bytes_read = varint(s[20:])

    addr_array = []

    for i in range(addresses):
        address = s[20 + bytes_read + 30*i: 20 + bytes_read + 30*(i+1)]

        # epoch = int(reverse(address[0:4]), 16)
        # date = strftime('%d/%m/%Y %H:%M:%S', localtime(epoch))

        # service = int(reverse(address[4:12]), 16)

        ip = hex_ip(address[12:28])
        port = int(b2a(address[28:30]), 16)

        addr_array.append((ip, port))

        return addr_array
