import os
import time
import math
import array
import pickle
import datetime
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
    return chksm


def make_pkt(nextseqnum, data, chksm):
    return [str(nextseqnum).encode(), data, chksm]


def udt_send(sndpkt, HOST = 'localhost', PORT = 12000):
    client_socket.sendto(sndpkt, (HOST, PORT))
    return


def refuse_data(data):
    return


def getacknum(rcvpkt):
    return int(rcvpkt[0].decode())


def rdt_rcv(rcvpkt):
    if rcvpkt:
        return True
    else:
        return False


def notcorrupt(rcvpkt, chksm):
    if rcvpkt[1] == chksm:
        return True
    else:
        return False


def corrupt(rcvpkt, chksm):
    if rcvpkt[1] == chksm:
        return False
    else:
        return True


HOST = 'localhost'
PORT = 12000
client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(0.01)

file_name = 'a.jpg'
file_data = open(file_name, 'rb')
data = rdt_send(file_data)
sndpkt_size = math.ceil(os.stat(file_name).st_size / 1024)

base = 0
nextseqnum = 0
N = 7
sndpkt = [None] * sndpkt_size
done = False
timeout = False

option = input('Selection option [ 1: No Error/ 2: ACK Error/ 3: Data Error/ 4: ACK Loss/ 5. Data Loss]: ')
ACK_ls = 0
ACK_err = 0
if int(option) in range(0, 6):
    if option.encode() == b'4':
        ACK_ls = 21
    elif option.encode() == b'2':
        ACK_err = 0
    option = option.encode()
else:
    option = b'1'

print(datetime.datetime.now())
udt_send(option)

while not done:
    if nextseqnum < base + N:
        chksm = checksum(data)
        sndpkt[nextseqnum] = pickle.dumps((make_pkt(nextseqnum, data, chksm)))
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
    rcvpkt = pickle.loads(rcvpkt)

    if rdt_rcv(rcvpkt) is True and notcorrupt(rcvpkt, chksm) is True:
        base = getacknum(rcvpkt) + 1
        if base == nextseqnum:
            stop_timer = time.time()
            if stop_timer - start_timer > 0.01:
                timeout = True
        else:
            start_timer = time.time()

    if rdt_rcv(rcvpkt) is True and corrupt(rcvpkt, chksm) is True:
        pass

    if nextseqnum == sndpkt_size:
        done = True
