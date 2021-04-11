import time
import array
import pickle
from socket import *

def rdt_send(data):
    return data.read(1024)


def checksum(data):
    if len(data) % 2 != 0:
        data += b'\0'
    byte = sum(array.array('H', data))
    byte = (byte >> 16) + (byte & 0xffff)
    byte += byte >> 16
    chksm = (~byte) & 0xffff
    chksm = str(chksm).encode()
    while len(chksm) < 5:
        chksm = b'0' + chksm
    return chksm


def make_pkt(nextseqnum, data, chksm):
    return ([str(nextseqnum).encode()], [data], [chksm])


def udt_send(sndpkt, HOST = 'localhost', PORT = 12000):
    client_socket.sendto(sndpkt, (HOST, PORT))
    return


def refuse_data(data):
    return


def getacknum(rcvpkt, index):
    return int(rcvpkt[:-index].decode())


def rdt_rcv(rcvpkt):
    if rcvpkt:
        return True
    else:
        return False


def notcorrupt(rcvpkt, checksum):
    index = len(checksum)
    checksum_recalc = rcvpkt[-index:]
    if checksum == checksum_recalc:
        return True
    else:
        return False


def corrupt(rcvpkt, checksum):
    index = len(checksum)
    checksum_recalc = rcvpkt[-index:]
    print(checksum_recalc)
    if checksum == checksum_recalc:
        return False
    else:
        return True


HOST = 'localhost'
PORT = 12000
client_socket = socket(AF_INET, SOCK_DGRAM)


file_data = open('b.jpg', 'rb')
data = rdt_send(file_data)

base = 0
nextseqnum = 0
sndpkt = []
N = 200
done = True
timeout = False

while True:
    if nextseqnum < base + N:
        chksm = checksum(data)
        sndpkt.append(make_pkt(nextseqnum, data, chksm))
        
        udt_send(sndpkt[nextseqnum])
        if base == nextseqnum:
            start_timer = time.time()
        nextseqnum += 1
        data = rdt_send(file_data)
    else:
        refuse_data(data)

    if timeout is True:
        start_timer = time.time()
        for base in range(nextseqnum - 1):
            udt_send(sndpkt[base])
        timeout = False

    rcvpkt, addr = client_socket.recvfrom(1024)
    if rdt_rcv(rcvpkt) is True and notcorrupt(rcvpkt, chksm) is True:
        base = getacknum(rcvpkt, len(chksm)) + 1
        if base == nextseqnum:
            stop_timer = time.time()
            if stop_timer - start_timer > 0.01:
                timeout = True
        else:
            start_timer = time.time()

    if rdt_rcv(rcvpkt) is True and corrupt(rcvpkt, chksm) is True:
        pass
