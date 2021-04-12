import array
import random
import pickle
from socket import *


def rdt_rcv(rcvpkt):
    if rcvpkt:
        print('True 1')
        return True
    else:
        return False


def notcorrupt(data, chksm):
    if checksum(data) == chksm:
        print('True 2')
        return True
    else:
        return False


def hasseqnum(extractedseqnum, expectedseqnum):
    if extractedseqnum == expectedseqnum:
        print('True 3')
        return True
    else:
        return False


def deliver_data(data):
    new_file.write(data)
    return


def checksum(data):
    if len(data) % 2 != 0:
        data += b'\0'
    chksm_recalc = sum(array.array('H', data))
    chksm_recalc = (chksm_recalc >> 16) + (chksm_recalc & 0xffff)
    chksm_recalc += chksm_recalc >> 16
    chksm_recalc = (~chksm_recalc) & 0xffff
    return str(chksm_recalc).encode()


def make_pkt(expectedseqnum, checksum):
    return [str(expectedseqnum).encode(), checksum]


def udt_send(sndpkt, addr):
    server_socket.sendto(sndpkt, addr)


def data_error(data, err_rate):
    err_chance = random.randint(1, 101)
    if err_chance < err_rate:
        print('TRIGGERED')
        l_shift_data = data[0:2]
        r_shift_data = data[2:]
        shifted_data = r_shift_data + l_shift_data
        data = shifted_data
    return data


def data_loss(rcvpkt, lss_rate):
    lss_chance = random.randint(1, 101)
    if lss_chance < lss_rate:
        print('TRIGGERED')
        rcvpkt = False
    return rcvpkt


HOST = 'localhost'
PORT = 12000
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((HOST, PORT))

expectedseqnum = 0
new_file = open('output.jpg', 'wb')

rcvpkt, addr = server_socket.recvfrom(2048)

data_err = 0
data_lss = 0
if rcvpkt == b'3':
    data_err = 20
elif rcvpkt == b'5':
    data_lss = 20

while True:
    rcvpkt, addr = server_socket.recvfrom(2048)

    rcvpkt = pickle.loads(rcvpkt)

    extractedseqnum = int(rcvpkt[0].decode())
    data            = data_error(rcvpkt[1], data_err)
    chksm           = rcvpkt[2]
    print(chksm)
    print(checksum(data))

    rcvpkt = data_loss(rcvpkt, data_lss)

    if rdt_rcv(rcvpkt) is True and notcorrupt(data, chksm) is True and hasseqnum(extractedseqnum, expectedseqnum) is True:
        deliver_data(data)
        sndpkt = pickle.dumps(make_pkt(expectedseqnum, checksum(data)))
        udt_send(sndpkt, addr)
        expectedseqnum += 1
    else:
        udt_send(sndpkt, addr)
