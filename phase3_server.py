import array
import random
from socket import *

HOST = 'localhost'
PORT = 12000
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((HOST, PORT))


def rebuild_checksum(data):
    if len(data) % 2 != 0:
        data += b'\0'

    byte = sum(array.array('H', data))
    byte = (byte >> 16) + (byte & 0xffff)
    byte += byte >> 16
    checksum_rebuilt = (~byte) & 0xffff

    while len(str(checksum_rebuilt)) != 5:
        checksum_rebuilt = '0' + str(checksum_rebuilt)

    return str(checksum_rebuilt).encode()


def make_corrupt(err_rate):
    ack = b'1'
    err_ceil = random.randint(1, 101)
    if err_ceil < err_rate:
        ack = b'0'
    return ack


while True:
    print('Waiting...')
    outputName, clientAddress = serverSocket.recvfrom(1024)           # Receive name of output file
    number_of_receives, addr = server_socket.recvfrom(2048)
    outputName = str(outputName, 'utf8')
    output = open('output_'+outputName, 'wb')
    number_of_receives = str(number_of_receives, 'utf8')
    print('Number of receives: ' + number_of_receives)
    print('Output File Name: '+ outputName)

    for receive in range(int(number_of_receives)):
        sequence_check = False
        checksum_check = False
        while sequence_check is False or checksum_check is False:
            print('Listening...')
            packet, addr = server_socket.recvfrom(2048)
            try:
                # Sequence: the first X bytes of the packet where X is the number of places in number_of_receives
                sequence = int(packet[:int(len(number_of_receives))].decode())
                # Checksum: the 5 bytes after the # of sequence bytes
                checksum = (packet[int(len(number_of_receives)):])[:5]
                # Payload: the bytes after the # of sequence bytes + the # of checksum bytes (5)
                payload = packet[(int(len(number_of_receives)) + 5):]
            except:
                sequence = 0
                checksum = b'0'
                payload = b'0'

            if sequence != receive:
                sequence_check = False
                print('Sequence failed!')
            else:
                sequence_check = True

            if checksum != rebuild_checksum(payload):
                checksum_check = False
                print('Checksum failed!')
            else:
                checksum_check = True

            if sequence_check is True and checksum_check is True:
                ack_corrupt = make_corrupt(5)
                server_socket.sendto(ack_corrupt, addr)
            else:
                print('Retrying...')

        output.write(payload)
        print('Packet [' + str(receive + 1) + '/' + str(number_of_receives) + ']')

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
### DATA CORRUPTION: Take rcvpkt[1:][:1024], assign it to a variable, and jumble it
def extract(rcvpkt):
    return rcvpkt[1:][:1024]

# Writes the extracted data to the file
def deliver_data(rcvpkt):
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
### ACK CORRUPTION: Take ACK and scramble it
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


print('Waiting...')

new_file = open('output.jpg', 'wb')

# This gets the loop started and allows it to continue internally
rcvpkt, addr = server_socket.recvfrom(2048)
oncethru = 0

while True:
    # "Try" is my attempt at closing out the server once it finished the image
    try:
        # @: Wait for 0 from below. If these trigger, GOTO "Wait for 1 from below."
        if rdt_rcv(rcvpkt) is True and notcorrupt(rcvpkt) is True and has_seq0(rcvpkt) is True:
                data = extract(rcvpkt)
                deliver_data(data)
                sndpkt = make_pkt(b'0', b'0', checksum(data))
                udt_send(sndpkt, addr)
                oncethru = 1

        # @: Wait for 1 from below. If these are all true, STAY @ "Wait for 1 from below."
        rcvpkt, addr = server_socket.recvfrom(2048)
        while rdt_rcv(rcvpkt) is True and (corrupt(rcvpkt) is True or has_seq0(rcvpkt) is True):
            udt_send(sndpkt, addr)
            rcvpkt, addr = server_socket.recvfrom(2048)

        # @: Wait for 1 from below. If these are all true, GOTO "Wait for 0 from below."
        if rdt_rcv(rcvpkt) is True and notcorrupt(rcvpkt) is True and has_seq1(rcvpkt) is True:
            data = extract(rcvpkt)
            deliver_data(data)
            sndpkt = make_pkt(b'1', b'1', checksum(data))
            udt_send(sndpkt, addr)

        # @: Wait for 0 from below. If these are all true, STY+AY @ "Wait for 0 from below."
        rcvpkt, addr = server_socket.recvfrom(2048)
        while rdt_rcv(rcvpkt) is True and (corrupt(rcvpkt) is True or has_seq1(rcvpkt) is True):
            if oncethru == 1:
                udt_send(sndpkt, addr)
            rcvpkt, addr = server_socket.recvfrom(2048)
    except ValueError:
        break

print('Done!')
