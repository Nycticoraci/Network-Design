import os
import math
import array
import random
import datetime
import time
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
        print("Expected Checksum: ", checksum)
        print("Received Checksum: ", checksum_recalc)
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

def ACK_error (rcvpkt, bitVal, loss_rate):
    err_chance = random.randint(1, 101)
    if err_chance < loss_rate:
        rcvpkt[:1] = bitVal
    return rcvpkt

# Simulates ACK loss by replacing ACK with the previous ACK
def ACK_loss(ack, ackPrev, loss_rate):
    err_chance = random.randint(1, 101)
    if err_chance < loss_rate:
        ack = ackPrev
    return ack

def seqValBtyes(seqVal):
    if (seqVal == 0):
        return b'0'
    elif (seqVal == 1):
        return b'1'
    elif (seqVal == 2):
        return b'2'
    elif (seqVal == 3):
        return b'3'
    elif (seqVal == 4):
        return b'4'
    elif (seqVal == 5):
        return b'5'
    elif (seqVal == 6):
        return b'6'
    elif (seqVal == 7):
        return b'7'
    elif (seqVal == 8):
        return b'8'
    elif (seqVal == 9):
        return b'9'
    else:
        print("Sequence Error")

def refuse_data(data):
    # DO NOTHING
    data = data

def getAckNum(rcvpkt):
    ACK = rcvpkt[:1]
    return ACK

# File name requested, then divided into 1024 bit chunks + remainder
file_name = input('Enter filename: ')
option    = input('Selection option [ 1: No Error/ 2: ACK Error/ 3: Data Error/ 4: ACK Loss/ 5. Data Loss]: ')
if option == '2':
    option = b'2'
elif option == '3':
    option = b'3'
elif option == '4':
    option = b'4'
elif option == '5':
    option = b'5'
else:
    option = b'1'

if option == b'4':
    ACK_ls  = 21
else:
    ACK_ls  = 0

if option == b'2':
    ACK_err  = 61
else:
    ACK_err = 0

file_size = os.stat(file_name).st_size
number_of_receives = math.ceil(file_size / 1024)

# Program starts at "call 0 from above"
call = 0

print(datetime.datetime.now())
rdt_send = read_file(file_name, number_of_receives)
udt_send(option)

prevpkt = 0

base = 1
nextSeqNum = 1
windowSize = 10
sndpkt = [0] * (number_of_receives + 10)
myTimer = [0] * (number_of_receives + 10)
# "Call from above"
for data in rdt_send:

    seqDivider = nextSeqNum / 10
    seqNumMod = nextSeqNum % 10
    seq = seqValBtyes(seqNumMod)
    if (nextSeqNum < base + windowSize):
        checksum = make_checksum(data)
        #print("Seq: ", seq)
        sndpkt[nextSeqNum] = make_pkt(seq, data, checksum)
        udt_send(sndpkt[nextSeqNum])
        if (base == nextSeqNum):
            myTimer[nextSeqNum] = time.time()
            #print("Time is: ", time.time())

        nextSeqNum += 1
    else:
        refuse_data(data)
    
    client_socket.settimeout(0.1)
    try:
        rcvpkt, addr = client_socket.recvfrom(1024)
    except:
        break

    if(rdt_rcv(rcvpkt) is True and corrupt(rcvpkt, checksum) is False):
        ackBytes = getAckNum(rcvpkt)
        ackInt = int.from_bytes(ackBytes, "little") - 48
        base = nextSeqNum + ackInt #+ 1 - 0.1
        #print("Not corrupt! :)")
        #print("Seq: ", seq)
        #print("Base: ", base)
        #print("Base: ", base)
        '''if(base == seq):
            timerStop = 1
        else:
            timerStop = 0
            startTimer = time.time()'''
    elif(time.time() - myTimer[nextSeqNum - 1] > 0.05):
        #print("Timeout!!")
        nval = 0
        while(base + nVal < nextSeqNum):
            udt_send(sndpkt[base + nVal])
            nVal += 1

   
print('Done.')
