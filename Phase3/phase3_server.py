import array
import random
from socket import *

HOST = 'localhost'
PORT = 12000
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((HOST, PORT))


# Determines if a packet has been successfully received
def rdt_rcv(rcvpkt):
    if rcvpkt:
        print('Received = true')
        return True
    else:
        print('Received = false')
        return False


# Compares the checksums and returns TRUE if they are NOT corrupt
def notcorrupt(rcvpkt):
    data = rcvpkt[1:][:1024]
    checksum = rcvpkt[1025:]
    byte = sum(array.array('H', data))
    byte = (byte >> 16) + (byte & 0xffff)
    byte += byte >> 16
    checksum_recalc = (~byte) & 0xffff
    checksum_recalc = str(checksum_recalc).encode()

    if checksum == checksum_recalc:
        print('Not corrupt = true')
        return True
    else:
        print('Not corrupt = false')
        return False


# Determines if the packet is sequence 0, returns TRUE if so
def has_seq0(rcvpkt):
    seq = rcvpkt[:1]
    if seq == b'0':
        print('Seq0 = true')
        return True
    else:
        print('Seq0 = false')
        return False


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


# Compares the checksums and returns TRUE if they ARE corrupt
def corrupt(data):
    data = rcvpkt[1:][:1024]
    checksum = rcvpkt[1025:]
    byte = sum(array.array('H', data))
    byte = (byte >> 16) + (byte & 0xffff)
    byte += byte >> 16
    checksum_recalc = (~byte) & 0xffff
    checksum_recalc = str(checksum_recalc).encode()

    if checksum == checksum_recalc:
        print('Corrupt = false')
        return False
    else:
        print('Corrupt = true')
        return True


# Determines if the packet is sequence 1, returns TRUE if so
def has_seq1(rcvpkt):
    seq = rcvpkt[:1]
    if seq == b'1':
        print('Seq1 = true')
        return True
    else:
        print('Seq1 = false')
        return False


def DATA_corrupt(data, err_rate):
    err_chance = random.randint(1, 101)
    if err_chance < err_rate:
        print('[DATA CORRUPTED]')
        l_shift_data = data[0:10]
        r_shift_data = data[10:]
        shifted_data = r_shift_data + l_shift_data
        data = shifted_data
    return data


def ACK_corrupt(ack, err_rate):
    err_chance = random.randint(1, 101)
    if err_chance < err_rate:
        print('[ACK CORRUPTED]')
        ack = b'2'
    return ack


print('Waiting...')

new_file = open('output.jpg', 'wb')

# This gets the loop started and allows it to continue internally
oncethru = 0

while True:
    while True:
        rcvpkt, addr = server_socket.recvfrom(2048)
        rcvpkt = DATA_corrupt(rcvpkt, 50)

        # @: Wait for 0 from below. If these trigger, GOTO "Wait for 1 from below."
        if rdt_rcv(rcvpkt) is True and notcorrupt(rcvpkt) is True and has_seq0(rcvpkt) is True:
            data = extract(rcvpkt)
            deliver_data(data)
            ACK = ACK_corrupt(b'0', 50)
            sndpkt = make_pkt(ACK, b'0', checksum(data))
            udt_send(sndpkt, addr)
            oncethru = 1
            break

        # @: Wait for 0 from below. If these are all true, STAY @ "Wait for 0 from below."
        if rdt_rcv(rcvpkt) is True and (corrupt(rcvpkt) is True or has_seq1(rcvpkt) is True):
            if oncethru == 1:
                udt_send(sndpkt, addr)

    while True:
        rcvpkt, addr = server_socket.recvfrom(2048)
        rcvpkt = DATA_corrupt(rcvpkt, 50)

        # @: Wait for 1 from below. If these are all true, GOTO "Wait for 0 from below."
        if rdt_rcv(rcvpkt) is True and notcorrupt(rcvpkt) is True and has_seq1(rcvpkt) is True:
            data = extract(rcvpkt)
            deliver_data(data)
            ACK = ACK_corrupt(b'1', 50)
            sndpkt = make_pkt(ACK, b'1', checksum(data))
            udt_send(sndpkt, addr)
            break

        # @: Wait for 1 from below. If these are all true, STAY @ "Wait for 1 from below."
        if rdt_rcv(rcvpkt) is True and (corrupt(rcvpkt) is True or has_seq0(rcvpkt) is True):
            udt_send(sndpkt, addr)
