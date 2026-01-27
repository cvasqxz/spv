import socket
import struct

def dns_query(domain, dns_server='8.8.8.8'):
    # Construir query DNS para un registro A
    tid = 0x1234  # ID de la consulta
    flags = 0x0100  # estándar
    qdcount = 1  # preguntas
    header = struct.pack('>HHHHHH', tid, flags, qdcount, 0, 0, 0)

    # Formatear dominio
    qname = b''
    for part in domain.split('.'):
        qname += struct.pack('B', len(part)) + part.encode()
    qname += b'\x00'
    qtype = 1  # A
    qclass = 1  # IN
    question = qname + struct.pack('>HH', qtype, qclass)

    packet = header + question

    # Socket UDP a DNS
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3)

    # MicroPython requires sockaddr format from getaddrinfo
    addr_info = socket.getaddrinfo(dns_server, 53, socket.AF_INET, socket.SOCK_DGRAM)
    sockaddr = addr_info[0][4]

    # MicroPython requires bytearray for socket.sendto()
    s.sendto(bytearray(packet), sockaddr)
    data, _ = s.recvfrom(512)
    s.close()

    # Parsear la respuesta (buscar tipo 1 clase 1 en las respuestas)
    rcode = (data[3] & 0x0F)
    if rcode != 0:
        raise Exception('DNS query failed with rcode %d' % rcode)

    ancount = struct.unpack('>H', data[6:8])[0]
    pos = 12   # después de header

    # Saltar el nombre de la pregunta
    while data[pos] != 0:
        pos += 1 + data[pos]
    pos += 5  # cero final + qtype + qclass (1+2+2)

    addrs = []
    for _ in range(ancount):
        # Saltar nombre/compression
        if data[pos] & 0xC0 == 0xC0:
            pos += 2
        else:
            while data[pos]:
                pos += 1 + data[pos]
            pos += 1
        typ, clas, ttl, rdlen = struct.unpack('>HHIH', data[pos:pos+10])
        pos += 10
        if typ == 1 and clas == 1 and rdlen == 4:
            ip_bytes = data[pos:pos+4]
            ip_addr = '.'.join(str(b) for b in ip_bytes)
            addrs.append(ip_addr)
        pos += rdlen
    return addrs

if __name__ == "__main__":
    # Ejemplo de uso:
    ips = dns_query('seed.bitcoin.wiz.biz')
    print("Respuestas DNS:")
    for ip in ips:
        print("  ", ip)