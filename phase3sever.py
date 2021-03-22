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
    number_of_receives, addr = server_socket.recvfrom(2048)
    new_file = open('output.jpg', 'wb')
    number_of_receives = str(number_of_receives, 'utf8')
    print('Number of receives: ' + number_of_receives)

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

        new_file.write(payload)
        print('Packet [' + str(receive + 1) + '/' + str(number_of_receives) + ']')
