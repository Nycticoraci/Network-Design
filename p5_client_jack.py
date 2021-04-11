import os
import math
import array
import random
import datetime
import time
from socket import *


def rdt_send(data):
    return data.read(1024)


# Combines the sequence, data, and checksum combined
def make_pkt(seq, data, checksum):
    return seq + data + checksum


# Computes the checksum from the data
def make_checksum(data):
    if len(data) % 2 != 0:
        data += b'\0'
    byte = sum(array.array('H', data))
    byte = (byte >> 16) + (byte & 0xffff)
    byte += byte >> 16
    checksum = (~byte) & 0xffff
    checksum = str(checksum).encode()
    return checksum


# Returns TRUE if packet is received, else FALSE
def rdt_rcv(rcvpkt):
    if rcvpkt:
        return True
    else:
        return False


# Returns TRUE if the server checksum matches the sent one, else FALSE
def corrupt(rcvpkt, checksum):
    checksum_recalc = rcvpkt[2:]
    if checksum == checksum_recalc:
        return False
    else:
        print("Expected Checksum: ", checksum)
        print("Received Checksum: ", checksum_recalc)
        return True


# Sends the packet
def udt_send(sndpkt, HOST='localhost', PORT=12000):
    client_socket.sendto(sndpkt, (HOST, PORT))
    return


def ACK_error(rcvpkt, loss_rate):
    err_chance = random.randint(1, 101)
    if err_chance < loss_rate:
        rcvpkt = b'x' + rcvpkt[1:]
    return rcvpkt


def ACK_loss(rcvpkt, loss_rate):
    err_chance = random.randint(1, 101)
    if err_chance < loss_rate:
        del rcvpkt[:1]
    return rcvpkt


def seqValBtyes(seqVal):
    if seqVal in range(0, 10):
        return str(seqVal).encode()
    else:
        print("Sequence Error")


def refuse_data(data):
    return


def getAckNum(rcvpkt):
    ACK = rcvpkt[:1]
    return ACK


HOST = 'localhost'
PORT = 12000
client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(2)


# File name requested, then divided into 1024 bit chunks + remainder
file_name = input('Enter filename: ')
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

file_data = open(file_name, 'rb')
data = rdt_send(file_data)
sndpkt_size = math.ceil(os.stat(file_name).st_size / 1024)

udt_send(option)

base = 1
nextSeqNum = 1
windowSize = 10
sndpkt = [0] * (sndpkt_size + 10)

while True:
    seqDivider = nextSeqNum / 10
    seqNumMod = nextSeqNum % 10
    seq = seqValBtyes(seqNumMod)

    if nextSeqNum < base + windowSize:
        checksum = make_checksum(data)
        print("Seq: ", seq)
        sndpkt[nextSeqNum] = make_pkt(seq, data, checksum)
        udt_send(sndpkt[nextSeqNum])
        if base == nextSeqNum:
            startTimer = time.time()

        nextSeqNum += 1
        data = rdt_send(file_data)
    else:
        refuse_data(data)

    try:
        try:
            rcvpkt, addr = client_socket.recvfrom(1024)
            rcvpkt = ACK_error(rcvpkt, ACK_err)
            rcvpkt = ACK_loss(rcvpkt, ACK_ls)
        except socket.timeout:
            for i in range(1, nextSeqNum - 1):
                udt_send(sndpkt[i])
            pass
    except TypeError:
        break

    if rdt_rcv(rcvpkt) is True and corrupt(rcvpkt, checksum) is False:
        ackBytes = getAckNum(rcvpkt)
        ackInt = int.from_bytes(ackBytes, "little") - 48
        base = nextSeqNum + ackInt
        print("Not corrupt!")
        print("Seq: ", seq)
        print("Base: ", base)
        if base == seq:
            timerStop = 1
        else:
            timerStop = 0
            startTimer = time.time()

print('Done.')
