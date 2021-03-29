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
# "Call from above"
for data in rdt_send:
    # If this is a call 0
    if call == 0:
        # Calcuate the checksum, order it sequence 0, and send w/ the data
        checksum = make_checksum(data)
        sndpkt = make_pkt(b'0', data, checksum)
        udt_send(sndpkt)
		
        # Initialize timer variables
        startTimer = time.time()
        inProgress = 1
        waitTime = 1
        
        while(inProgress == 1):
            # Compares current time to the start
            timePassed = time.time() - startTimer

            # Sets reset to 0, in case it had been 1 in the previous iteration
            reset = 0

            # Checks if the amount of time has exceeded the wait time
            if timePassed >= waitTime:
                # Signals that the packet should be resent
                reset = 1   
                
            # If the packet is received but data or ACK is corrupt, repeat.
            # When none of them are corrupt, call will change to 1 and move on
            if (reset == 0):
                client_socket.settimeout(0.1)
                try:
                    rcvpkt, addr = client_socket.recvfrom(1024)
                    rcvpkt = ACK_error(rcvpkt, b'2', ACK_err)
                    savepkt = rcvpkt
                    rcvpkt = ACK_loss(rcvpkt, prevpkt, ACK_ls)
                    prevpkt = savepkt
                except:
                    break
                
                if rdt_rcv(rcvpkt) is True and (corrupt(rcvpkt, checksum) is False and isACK(rcvpkt, b'1') is False):
                    # Packet is received, so now the while-loop can end
                    inProgress = 0
                    
                elif rdt_rcv(rcvpkt) is True and ((corrupt(rcvpkt, checksum) is True) or isACK(rcvpkt, b'0') is False):
                    # If packet is corrupt, there's no need in waiting for the timeout, so we signal for an early timeout
                    reset = 1
            
            if (inProgress == 1 & reset == 1):
                # Send the packet again, and reset the timer
                udt_send(sndpkt)
                startTimer = time.time()

        # Next call will be 1
        call = 1

    # If this is a call 1
    elif call == 1:
        # Calcuate the checksum, order it sequence 1, and send w/ the data
        checksum = make_checksum(data)
        sndpkt = make_pkt(b'1', data, checksum)
        udt_send(sndpkt)

        # Initialize timer variables
        startTimer = time.time()
        inProgress = 1
        waitTime = 1

        while(inProgress == 1):
            # Compares current time to the start
            timePassed = time.time() - startTimer

            # Sets reset to 0, in case it had been 1 in the previous iteration
            reset = 0

            # Checks if the amount of time has exceeded the wait time
            if timePassed >= waitTime:
                # Signals that the packet should be resent
                reset = 1
                            
            if(reset == 0):
                # If the packet is received but data or ACK is corrupt, repeat.
                # When none of them are corrupt, call will change to 1 and move on
                client_socket.settimeout(0.1)
                try:
                    rcvpkt, addr = client_socket.recvfrom(1024)
                    rcvpkt = ACK_error(rcvpkt, b'2',ACK_err)
                    savepkt = rcvpkt
                    rcvpkt = ACK_loss(rcvpkt, prevpkt, ACK_ls)
                    prevpkt = savepkt
                except:
                    break
            
                if rdt_rcv(rcvpkt) is True and (corrupt(rcvpkt, checksum) is False and isACK(rcvpkt, b'0') is False):
                    # Packet is received, so now the while-loop can end
                    inProgress = 0

                elif rdt_rcv(rcvpkt) is True and ((corrupt(rcvpkt, checksum) is True) or isACK(rcvpkt, b'1') is False):
                    # If packet is corrupt, there's no need in waiting for the timeout, so we signal for an early timeout
                    reset = 1
                
            if(inProgress == 1 & reset == 1):
                # Send the packet again, and reset the timer
                udt_send(sndpkt)
                startTimer = time.time()
        # Next call will be 0
        call = 0
        
print('Done.')
