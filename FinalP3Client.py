import os
import math
import array
import random
import datetime
from socket import *

HOST = 'localhost'
PORT = 12000
client_socket = socket(AF_INET, SOCK_DGRAM)


# Opens the file, reads it in bytes, and puts 1024 bit chunks into a list
def read_file(data, size):
    packet_list = []
    user_file = open(data, 'rb')
    payload = user_file.read(1024)
    for i in range(size):
        packet_list.append(payload)
        payload = user_file.read(1024)
    return packet_list


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
        return True


# Sends the packet
def udt_send(sndpkt, HOST = 'localhost', PORT = 12000):
    client_socket.sendto(sndpkt, (HOST, PORT))
    return


# Returns TRUE if the ACk macthes the expected value, else FALSE
def isACK(rcvpkt, check):
    ACK = rcvpkt[:1]
    if ACK == check:
        return True
    else:
        return False


# File name requested, then divided into 1024 bit chunks + remainder
file_name = input('Enter filename: ')
option    = input('Selection option [1/2/3]: ')
if option == '2':
    option = b'2'
elif option == '3':
    option = b'3'
else:
    option = b'1'
file_size = os.stat(file_name).st_size
number_of_receives = math.ceil(file_size / 1024)

# Program starts at "call 0 from above"
call = 0

print(datetime.datetime.now())
rdt_send = read_file(file_name, number_of_receives)
udt_send(option)

# "Call from above"
for data in rdt_send:
    # If this is a call 0
    if call == 0:
        # Calcuate the checksum, order it sequence 0, and send w/ the data
        checksum = make_checksum(data)
        sndpkt = make_pkt(b'0', data, checksum)
        udt_send(sndpkt)

        # If the packet is received but data or ACK is corrupt, repeat.
        # When none of them are corrupt, call will change to 1 and move on
        client_socket.settimeout(0.1)
        try:
            rcvpkt, addr = client_socket.recvfrom(1024)
        except:
            break

        while rdt_rcv(rcvpkt) is True and (corrupt(rcvpkt, checksum) is True or isACK(rcvpkt, b'1') is True):
            udt_send(sndpkt)
            client_socket.settimeout(0.1)
            try:
                rcvpkt, addr = client_socket.recvfrom(1024)
            except:
                break
                rcvpkt, addr = client_socket.recvfrom(1024)

        # Next call will be 1
        call = 1

    # If this is a call 1
    elif call == 1:
        # Calcuate the checksum, order it sequence 1, and send w/ the data
        checksum = make_checksum(data)
        sndpkt = make_pkt(b'1', data, checksum)
        udt_send(sndpkt)

        # If the packet is received but data or ACK is corrupt, repeat.
        # When none of them are corrupt, call will change to 1 and move on
        client_socket.settimeout(0.1)
        try:
            rcvpkt, addr = client_socket.recvfrom(1024)
        except:
            break

        while rdt_rcv(rcvpkt) is True and (corrupt(rcvpkt, checksum) is True or isACK(rcvpkt, b'0') is True):
            udt_send(sndpkt)
            client_socket.settimeout(0.1)
            try:
                rcvpkt, addr = client_socket.recvfrom(1024)
            except:
                break

        # Next call will be 0
        call = 0
        
print('Done.')
