import os
import time
import math
import array
import random
from socket import *

serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

file_name = input('Enter filename: ')


def make_packet(packet, data):
    packet_list = []
    user_file = open(data, 'rb')
    payload = user_file.read(1024)

    for sequence in range(packet):
        while len(str(packet)) != len(str(sequence)):
            sequence = '0' + str(sequence)

        if len(payload) % 2 != 0:
            payload += b'\0'
        res = sum(array.array("H", payload))
        res = (res >> 16) + (res & 0xffff)
        res += res >> 16
        checksum = (~res) & 0xffff

        while len(str(checksum)) != 5:
            checksum = '0' + str(checksum)

        packet_list.append(str(sequence).encode() + str(checksum).encode() + payload)
        print(packet_list[int(sequence)])
        payload = user_file.read(1024)
    return packet_list


file_size = os.stat(file_name).st_size
NR = str(math.ceil(file_size / 1024))
print('Number of Receives is ' + NR)
number_receives = NR.encode('utf8')
clientSocket.sendto(number_receives, (serverName, serverPort))

rdt_send = make_packet(int(NR), file_name)

for packet_to_send in rdt_send:
    clientSocket.sendto(packet_to_send, (serverName, serverPort))
    time.sleep(0.02)

clientSocket.close()
