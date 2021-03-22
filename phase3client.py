import os
import math
import array
import random
from socket import *

HOST = 'localhost'
PORT = 12000
client_socket = socket(AF_INET, SOCK_DGRAM)

file_name = input('Enter filename: ')


# "Packet" is the number of the packet being sent, and "data" is the image
def make_packet(packet, data):
    packet_list = []
    user_file = open(data, 'rb')
    payload = user_file.read(1024)

    # The sequence number comes from the total number of packets sent
    for sequence in range(packet):

        # This prepends 0s to the sequence number so it's the same number of digits each time
        while len(str(packet)) != len(str(sequence)):
            sequence = '0' + str(sequence)

        # If the length of the payload is uneven, add a 0
        if len(payload) % 2 != 0:
            payload += b'\0'

        # These operations create the checksum number
        byte = sum(array.array('H', payload))
        byte = (byte >> 16) + (byte & 0xffff)
        byte += byte >> 16
        checksum = (~byte) & 0xffff

        # Checksum is a maximum of 5 digits long; this prepends digits to checksums < 5
        while len(str(checksum)) != 5:
            checksum = '0' + str(checksum)

        # This encodes the sequence and checksum; the payload is already encoded. This makes the full packet
        packet_list.append(str(sequence).encode() + str(checksum).encode() + payload)
        payload = user_file.read(1024)

    # Returns a list where each index is a new packet
    return packet_list


def make_corrupt(data_packet, err_ceil):
    err_rate = random.randint(1, 101)
    if err_rate < err_ceil:
        l_err_first  = data_packet[0:10]
        l_err_second = data_packet[10:]
        data_packet = l_err_second + l_err_first
    return data_packet


def is_ack(packet):
    if packet == b'1':
        return True
    else:
        return False


file_size = os.stat(file_name).st_size
number_of_receives = str(math.ceil(file_size / 1024))
print('Number of receives is ' + number_of_receives)
number_receives = number_of_receives.encode('utf8')
client_socket.sendto(number_receives, (HOST, PORT))

image_data = make_packet(int(number_of_receives), file_name)

for packet_data in image_data:
    success = False
    while success is False:
        print(packet_data)
        packet_corrupt = make_corrupt(packet_data, 1)
        client_socket.sendto(packet_corrupt, (HOST, PORT))
        client_socket.settimeout(1)
        try:
            packet, addr = client_socket.recvfrom(1024)
        except:
            continue

        if is_ack(packet) is True:
            success = True
            print('Success!')
        else:
            print('Resending...')
            print(packet_data)


client_socket.close()
