import array
import random
import tkinter as tk
from tkinter import simpledialog
from socket import *

HOST = 'localhost'
PORT = 12000
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((HOST, PORT))



def scn_rcv():
    root = tk.Tk()
    root.withdraw()
    scenario = simpledialog.askstring(title = 'Server Input',
                                  prompt = 'What scenario would you like? (1: Normal Process, 2: Data Corruption, 3: ACK Corruption')
    scen = int(scenario)
    
    if scen == 1:
        print ('def1')
        rate = 0
        ack_err = 0
        return scen, rate, ack_err
    elif scen == 2:
        rate = simpledialog.askstring(title = 'Server Input',
                                  prompt = 'What percentage error/loss would you like? ')
       # rate = input('What percentage error/loss would you like? ')
        rate = int(rate)
        ack_err = 0
        print ('def2')
        return scen, rate, ack_err
    elif scen == 3:
        ack_err = simpledialog.askstring(title = 'Server Input',
                                  prompt = 'What percentage ack error would you like? ')
        #ack_err = input('What percentage ack error would you like? ')
        ack_err = int(ack_err)
        rate = 0
        print ('def3')
        return scen, rate, ack_err
    else:
        print ('no scenario')
        return

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
    
# Extracts the data from the packet and returns it
### DATA CORRUPTION: Take data[1:][:1024], assign it to a variable, and jumble it
#### When calling function, put 'rate' instead of number for err_ceil
def make_datacorrupt(data, err_ceil):
    err_rate = random.randint(1, 101)
    if err_rate < err_ceil:
        l_err_first  = data[0:10]
        l_err_second = data[10:]
        data = l_err_second + l_err_first
    return data

### ACK CORRUPTION: Take ACK and scramble it
#### When calling function, put 'ack_err' in parentheses instead of a number for err_rate
def make_ackcorrupt(err_rate):
    ack = b'1'
    err_ceil = random.randint(1, 101)
    if err_ceil < err_rate:
        ack = b'0'
    return ack

print('Waiting...')

new_file = open('output.jpg', 'wb')

# Calls Scenario If statement
scenChoice, dataError, ackError = scn_rcv() # JF - The function outputs 3 variables to make it clearer
print(scenChoice, dataError, ackError)


# This gets the loop started and allows it to continue internally
rcvpkt, addr = server_socket.recvfrom(2048)
rcvpkt = make_datacorrupt(rcvpkt,dataError) #JF - Corrupts data depending on error rate dataError
oncethru = 0


while True:
    # "Try" is my attempt at closing out the server once it finished the image
    try:
        # @: Wait for 0 from below. If these trigger, GOTO "Wait for 1 from below."
        if rdt_rcv(rcvpkt) is True and notcorrupt(rcvpkt) is True and has_seq0(rcvpkt) is True:
                print('Valid Data')
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
            #if (notcorrupt(rcvpkt) is True):
            #   vdata = extract(rcvpkt)
            #    deliver_data(data)
            #    sndpkt = make_pkt(b'0', b'0', checksum(data))
            #    udt_send(sndpkt, addr)
            #    oncethru = 1

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
