import array
import random
import pickle
from socket import *

# This script uses "pickle." It is a module that allows lists to be sent intact over sockets.


# If a packet is not lost, return true, else, false
def rdt_rcv(rcvpkt):
    if rcvpkt:
        return True
    else:
        return False


# If the recomputed checksum equals the one sent in the packet, return true, else, false
def notcorrupt(data, chksm):
    if data == chksm:
        return True
    else:
        return False


# Checks the sequence # from the packet and compares it to the serverside expected value
def hasseqnum(extractedseqnum, expectedseqnum):
    if extractedseqnum == expectedseqnum:
        return True
    else:
        return False


# Writes the confirmed data to the file
def deliver_data(data):
    new_file.write(data)
    return


# (Re)calculates the checksum given byte data (appends a "0" to the end if indivisible by 2)
def checksum(data):
    if len(data) % 2 != 0:
        data += b'\0'
    chksm_recalc = sum(array.array('H', data))
    chksm_recalc = (chksm_recalc >> 16) + (chksm_recalc & 0xffff)
    chksm_recalc += chksm_recalc >> 16
    chksm_recalc = (~chksm_recalc) & 0xffff
    return str(chksm_recalc).encode()


# Makes the ACK packet using the confirmed expected number and the recalculated checksum
def make_pkt(expectedseqnum, checksum):
    return [str(expectedseqnum).encode(), checksum]


# Sends the data it is given and returns
def udt_send(sndpkt, addr):
    server_socket.sendto(sndpkt, addr)


# If the random chance triggers, the data will be "corrupted" to be 1025 bytes of "0001" (an impossible value otherwise)
def data_error(data, err_rate):
    err_chance = random.randint(1, 101)
    if err_chance < err_rate:
        data = b'1' * 1025
    return data


# If the random chance triggers, deletes the data packet
def data_loss(rcvpkt, lss_rate):
    lss_chance = random.randint(1, 101)
    if lss_chance < lss_rate:
        rcvpkt = False
    return rcvpkt


HOST = 'localhost'
PORT = 12000
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((HOST, PORT))

expectedseqnum = 0
new_file = open('output.jpg', 'wb')

option, addr = server_socket.recvfrom(2048)

# Data error and loss default to 0
data_err = 0
data_lss = 0
# If the received value is either 3 or 5, adjust the data error/loss accordingly
if option == b'3':
    data_err = 70
elif option == b'5':
    data_lss = 70

# MAIN FSM LOOP STARTS HERE
while True:
    # Receives the packet
    rcvpkt, addr = server_socket.recvfrom(2048)

    # The client sends "EOF" when the last packet has been ACK'd and the server knows it can close the output file
    if rcvpkt == b'EOF':
        break

    # Breaks the data into its principle parts (sequence number, data, checksum) and recalculates checksum from the data
    rcvpkt          = pickle.loads(rcvpkt)
    extractedseqnum = int(rcvpkt[0].decode())           # Automatically converts the byte value to an int
    data            = data_error(rcvpkt[1], data_err)   # Corruption function is built in to the data extraction
    chksm           = rcvpkt[2]
    chksm_recalc    = checksum(data)

    rcvpkt = data_loss(rcvpkt, data_lss)                # Data loss is calculated after to avoid NoneType packet errors

    # The main conditional for the sender via the FSM
    if rdt_rcv(rcvpkt) is True and notcorrupt(chksm_recalc, chksm) is True and hasseqnum(extractedseqnum, expectedseqnum) is True:
        deliver_data(data)
        sndpkt = pickle.dumps(make_pkt(expectedseqnum, chksm_recalc))
        udt_send(sndpkt, addr)
        expectedseqnum += 1
    else:
        # This error triggers if the very first packet gets corrupted and sndpkt() hasn't had a chance to be made once
        try:
            # "Default" (as seen on the FSM)
            udt_send(sndpkt, addr)
        except NameError:
            pass

new_file.close()
print('Done.')
