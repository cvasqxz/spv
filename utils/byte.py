from binascii import a2b_hex, b2a_hex


def b2a(s):
    return b2a_hex(s).decode()


def reverse(s):
    if type(s) is str:
        bs = a2b_hex(s)
    elif type(s) is bytes:
        bs = s
    else:
        return b''

    return b2a(bs[::-1])

def hex_ip(s):
    ipv = s.strip(b'\x00')
    ip = str(ipv[-4]) + '.' + str(ipv[-3]) + '.' + \
        str(ipv[-2]) + '.' + str(ipv[-1])
    return ip


def varint(s):
    if s[0] < 0xFD:
        return s[0], 1
        
    off = 2**(s[0] - 0xFC)
    output = int.from_bytes(s[1:1+off], "little")
    
    return output - 1, off + 2
