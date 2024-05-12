from socket import (socket, 
                    AF_INET, 
                    SOCK_DGRAM)

from Helpers import *

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(("localhost", 1255))

c = 0

while True:
    packet, address = sock.recvfrom(256)
    print(Unpack(packet))
    if c % 11:
        sock.sendto(packet[:16], address)
        
    c += 1
    if int(packet[16]) == 1:
        break
