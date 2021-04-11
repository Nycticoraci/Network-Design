import array
import pickle
from socket import *


def rdt_rcv(rcvpkt):
    if rcvpkt:
        return True
    else:
        return False


def notcorrupt(data, chksm):
    if chksm == checksum(data):
        return True
    else:
        return False


def hasseqnum(extractedseqnum, expectedseqnum):
    if extractedseqnum == expectedseqnum:
        return True
    else:
        return False


def deliver_data(data):
    print(data)
    new_file.write(data)
    return


def checksum(data):
    if len(data) % 2 != 0:
        data += b'\0'
    byte = sum(array.array('H', data))
    byte = (byte >> 16) + (byte & 0xffff)
    byte += byte >> 16
    checksum_recalc = (~byte) & 0xffff
    checksum_recalc = str(checksum_recalc).encode()
    return checksum_recalc


def make_pkt(expectedseqnum, checksum):
    return [str(expectedseqnum).encode(), checksum]


def udt_send(sndpkt, addr):
    server_socket.sendto(sndpkt, addr)


def extract_data(rcvpkt):
    return int(rcvpkt[0].decode()), rcvpkt[1], rcvpkt[2]


HOST = 'localhost'
PORT = 12000
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((HOST, PORT))

expectedseqnum = 0
new_file = open('output.jpg', 'wb')
rcvpkt, addr = server_socket.recvfrom(2048)

while True:
    rcvpkt, addr = server_socket.recvfrom(2048)
    rcvpkt = pickle.loads(rcvpkt)
    extractedseqnum, data, chksm = extract_data(rcvpkt)
    if rdt_rcv(rcvpkt) is True and notcorrupt(data, chksm) is True and hasseqnum(extractedseqnum, expectedseqnum) is True:
        deliver_data(data)
        sndpkt = pickle.dumps(make_pkt(expectedseqnum, checksum(data)))
        udt_send(sndpkt, addr)
        expectedseqnum += 1
    else:
        udt_send(sndpkt, addr)
