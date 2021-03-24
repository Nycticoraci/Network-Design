from socket import *
import time, os, subprocess, math, array, random
import tkinter as tk
from tkinter import simpledialog

HOST = 'localhost'
PORT = 12000
SOCK = socket(AF_INET, SOCK_DGRAM)

def read_file(data, size):
    packet_list = []
    user_file = open(data, 'rb')
    payload = user_file.read(1024)
    for i in range(size):
        packet_list.append(payload)
        payload = user_file.read(1024)
    return packet_list

def make_pkt(seq, data, checksum):
    return seq + data + checksum

def make_checksum(data):
    if len(data) % 2 != 0:
        data += b'\0'
    byte = sum(array.array('H', data))
    byte = (byte >> 16) + (byte & 0xffff)
    byte += byte >> 16
    checksum = (~byte) & 0xffff
    checksum = str(checksum).encode()
    return checksum

def rdt_rcv(rcvpkt):
    if rcvpkt:
        print('Received = true')
        return True
    else:
        print('Received = false')
        return False

def corrupt(rcvpkt, checksum):
    checksum_recalc = rcvpkt[2:]
    if checksum == checksum_recalc:
        print('Corrupt = false')
        return False
    else:
        print('Corrupt = true')
        return True

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

def is_os(path):
    linux = subprocess.run(['uname'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #print(linux.returncode)
    if linux.returncode == 0:
        i = path.rfind('/')                             #If uname completes successfully (return code 0), linux env is true
    else:                                               #else run path for windows
        i = path.rfind('\\')
    return i                                            #return index of last path (filename)

def option(i):
        if i == 0:
            rate = 1
            print(rate)
        elif i == 1:
            rate = 50
            print (rate)
        elif i == 2:
            SOCK.sendto(str(i).encode('utf8'), (HOST, PORT))
        return i

## MAIN ##
# Creates simple popup GUI
root = tk.Tk()
root.withdraw()
button0 = tk.Button(root, text='0: Normal Process', width=20, command=option(0))
button0.pack()
button1 = tk.Button(root, text='1: Data Corruption', width=20, command=option(1))
button1.pack()
button2 = tk.Button(root, text='2: ACK Corruption', width=20, command=option(2))
button2.pack()
path = simpledialog.askstring(title = 'Client Input', prompt = 'Hello friend! What is the path for your file?')


print('File name is: '+ path[is_os(path)+1:])         #Verify user input is correct
print('File path is: '+ path)
output = path[is_os(path)+1:].encode('utf8')          #Encode file name
SOCK.sendto(output,(HOST, PORT))                      #Send file name to server
time.sleep(0.02)                                      # Pause the process so that the server does not mix up the packets for file name and fize size

file_size = os.stat(path).st_size                     # Gets size of the file in bytes
NR = str(math.ceil(file_size / 1024))                 # Returns ceiling of filesize divided by 1024
print('Number of Receives is ' + NR)                  # Prints number of packets to send
number_receives = NR.encode('utf8')
SOCK.sendto(number_receives,(HOST, PORT))    # Sends number to server

call = 0
rdt_send = read_file(file_name, number_of_receives)

for data in rdt_send:
    if call == 0:
        checksum = make_checksum(data)
        sndpkt = make_pkt(b'0', data, checksum)
        udt_send(sndpkt)

        rcvpkt, addr = client_socket.recvfrom(1024)
        while rdt_rcv(rcvpkt) is True and (corrupt(rcvpkt, checksum) is True or isACK(rcvpkt, b'1') is True):
            udt_send(sndpkt)
            rcvpkt, addr = client_socket.recvfrom(1024)

        call = 1

    elif call == 1:
        checksum = make_checksum(data)
        sndpkt = make_pkt(b'1', data, checksum)
        udt_send(sndpkt)

        rcvpkt, addr = client_socket.recvfrom(1024)
        while rdt_rcv(rcvpkt) is True and (corrupt(rcvpkt, checksum) is True or isACK(rcvpkt, b'0') is True):
            udt_send(sndpkt)
            rcvpkt, addr = client_socket.recvfrom(1024)

        call = 0

    print('\n')
SOCK.close()
