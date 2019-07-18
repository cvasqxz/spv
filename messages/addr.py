from utils.byte import varint, reverse, int_hex, hex_ip
from utils.log import log_print
from binascii import b2a_hex
from time import time, strftime, localtime

def parse_addr(s):
    addresses = varint(s[20:])
    log_print('addr', '%i received' % addresses)

    for i in range(addresses):
        address = s[21 + 30*i: 21 + 30*(i+1)]
        
        epoch = int(reverse(address[0:4]), 16)
        date = strftime('%d/%m/%Y %H:%M:%S', localtime(epoch))
    
        service = int(reverse(address[4:12]), 16)
        
        ip = hex_ip(address[12:28])
        port = str(int(b2a_hex(address[28:30]), 16))

        log_print('new addr', ip + ':' + port + ' (%s)' % date)