from socket import *
import time
import os
import math

serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
fileName = str(input('Hello friend! What is the name of the file?'))

def Make_Packet(packet, data):
    packet_list = []
    userFile = open(data, 'rb')
    packet_size = userFile.read(1024)
    for i in range(packet):
        packet_list.append(packet_size)
        packet_size = userFile.read(1024)
    return packet_list

file_size = os.stat(fileName).st_size        # Gets size of the file in bytes
NR = str(math.ceil(file_size / 1024))        # Returns ceiling of filesize divided by 1024
print('Number of Receives is ' + NR)         # Prints number of packets to send
number_receives = NR.encode('utf8')
clientSocket.sendto(number_receives,(serverName, serverPort))    # Sends number to server

rdt_send = Make_Packet(int(NR), fileName)

for packet in rdt_send:
    clientSocket.sendto(packet,(serverName, serverPort))
    time.sleep(0.02)
clientSocket.close()