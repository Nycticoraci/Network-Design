import os
import math
import array
import random
import tkinter as tk
from tkinter import simpledialog
from socket import *

HOST = 'localhost'
PORT = 12000
client_socket = socket(AF_INET, SOCK_DGRAM)

# Creates simple popup GUI
root = tk.Tk()
root.withdraw()
file_name = simpledialog.askstring(title = 'Client Input',
                                  prompt = 'Hello friend! What is the path for your file?')

# Reads data (aka payload) from the file and adds it to packet_list
def read_file(data, size):
    packet_list = []
    user_file = open(data, 'rb')
    payload = user_file.read(1024)
    for i in range(size):
        packet_list.append(payload)
        payload = user_file.read(1024)
    return packet_list

# Combines the sequence number and Checksum with the data, so they become one combined packet
def make_pkt(seq, data, checksum):
    return seq + data + checksum

# Calculates Checksum to send to Server
def make_checksum(data):
    if len(data) % 2 != 0: # Makes sure that the data has an even number of bytes
        data += b'\0'
    byte = sum(array.array('H', data))
    byte = (byte >> 16) + (byte & 0xffff)
    byte += byte >> 16
    checksum = (~byte) & 0xffff
    checksum = str(checksum).encode()
    return checksum

# Checks if packet is received or not
def rdt_rcv(rcvpkt):
    if rcvpkt:
        print('Received = true')
        return True
    else:
        print('Received = false')
        return False

# Checks if the Received packet's Checksum is equal to the expected Checksum
def corrupt(rcvpkt, checksum):
    checksum_recalc = rcvpkt[2:]
    if checksum == checksum_recalc:
        print('Corrupt = false')
        return False
    else:
        print('Corrupt = true')
        return True

# Sending a packet via UDP Sockets
def udt_send(sndpkt, HOST = 'localhost', PORT = 12000):
    client_socket.sendto(sndpkt, (HOST, PORT))
    return


def isACK(rcvpkt, check):
    ACK = rcvpkt[:1]
    if ACK == check:
        print('ACK Check = true')
        return True
    else:
        print('ACK Check = false')
        return False



file_size = os.stat(file_name).st_size
number_of_receives = math.ceil(file_size / 1024)
print('Number of receives is ' + str(number_of_receives))
call = 0

rdt_send = read_file(file_name, number_of_receives)

for data in rdt_send:
    if call == 0:
        checksum = make_checksum(data)
        sndpkt = make_pkt(b'0', data, checksum)
        udt_send(sndpkt)

        rcvpkt, addr = client_socket.recvfrom(1024)
        while rdt_rcv(rcvpkt) is True and isACK(rcvpkt, b'1') is True: #and (corrupt(rcvpkt, checksum) is True or
            udt_send(sndpkt)
            rcvpkt, addr = client_socket.recvfrom(1024)

        call = 1

    elif call == 1:
        checksum = make_checksum(data)
        sndpkt = make_pkt(b'1', data, checksum)
        udt_send(sndpkt)

        rcvpkt, addr = client_socket.recvfrom(1024)
        while rdt_rcv(rcvpkt) is True and isACK(rcvpkt, b'0') is True: #and (corrupt(rcvpkt, checksum) is True or
            udt_send(sndpkt)
            rcvpkt, addr = client_socket.recvfrom(1024)

        call = 0

print('end\n')
