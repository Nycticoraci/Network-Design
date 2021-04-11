import array
import random
import datetime
from socket import *


# Determines if a packet has been successfully received
def rdt_rcv(rcvpkt):
    if rcvpkt:
        return True
    else:
        return False


# Compares the checksums and returns TRUE if they are NOT corrupt
def notcorrupt(rcvpkt):
    try:
        if rcvpkt[1025:] == checksum(rcvpkt[1:][:1024]):
            return True
        else:
            return False
    except ValueError:
        print('Done.')
        print(datetime.datetime.now())
        exit()


# Extracts the data from the packet and returns it
def extract(rcvpkt):
    return rcvpkt[1:][:1024]


# Writes the extracted data to the file
def deliver_data(data):
    new_file.write(data)
    return


# Calculates and returns the checksum from the received data
def checksum(rcvpkt):
    byte = sum(array.array('H', rcvpkt))
    byte = (byte >> 16) + (byte & 0xffff)
    byte += byte >> 16
    checksum_recalc = (~byte) & 0xffff
    checksum_recalc = str(checksum_recalc).encode()
    return checksum_recalc


# Makes the packet consisting of the ACK (0 or 1), level (0 or 1), and checksum
def make_pkt(ACK, seq, checksum):
    return ACK + b'0' + checksum


# Sends the packet at the address
def udt_send(sndpkt, addr):
    server_socket.sendto(sndpkt, addr)


def DATA_corrupt(data, err_rate):
    err_chance = random.randint(1, 101)
    if err_chance < err_rate:
        l_shift_data = data[0:10]
        r_shift_data = data[10:]
        shifted_data = r_shift_data + l_shift_data
        data = shifted_data
    return data


def DATA_loss(data, loss_rate):
    err_chance = random.randint(1, 101)
    if err_chance < loss_rate:
        data = b''
    return data


def seqValBtyes(seqVal):
    if seqVal in range(0, 10):
        return str(seqVal).encode()
    else:
        print("Sequence Error")


def has_seq(rcvpkt, expectedSeq):
    seq = rcvpkt[:1]
    if seq == expectedSeq:
        return True
    else:
        return False


HOST = 'localhost'
PORT = 12000
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print('Waiting...')

# Selects the option
option, addr = server_socket.recvfrom(2048)

# Option 1: No errors. 2: 20% chance ACk corrupt. 3: 20% chance data corrupt.
DATA_ls = 0
DATA_err = 0
if option == b'3':
    DATA_err = 21
    print('21')
elif option == b'5':
    DATA_ls = 21

new_file = open('output.jpg', 'wb')

prevpkt = 0
expectedSeqNum = 1

while True:
    while True:
        seqNumMod = expectedSeqNum % 10
        expectedSeq = seqValBtyes(seqNumMod)
        rcvpkt, addr = server_socket.recvfrom(2048)
        rcvpkt = DATA_corrupt(rcvpkt, DATA_err)
        rcvpkt = DATA_loss(rcvpkt, DATA_ls)

        if rdt_rcv(rcvpkt) is True and notcorrupt(rcvpkt) is True and has_seq(rcvpkt, expectedSeq) is True:
            print("If is executing")
            data = extract(rcvpkt)
            deliver_data(data)
            ACK = expectedSeq
            sndpkt = make_pkt(ACK, expectedSeq, checksum(data))
            udt_send(sndpkt, addr)
            expectedSeqNum += 1
            break
        else:
            print("Else is executing", rdt_rcv(rcvpkt), notcorrupt(rcvpkt), has_seq(rcvpkt, expectedSeq))
            udt_send(sndpkt, addr)
