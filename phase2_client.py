from socket import *
import time
import os
import math

serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
fileName = str(input('Hello friend! What is the name of the file?'))

# If this function is told to div[ide], it divides the filsize by 2014 (rounded up)
# If this function is told to send, it sends the packets in units of 1024 bytes
def Make_Packet(file, func):
    if func == 'div':
        file_stats = os.stat(file).st_size        # Gets size of the file in bytes
        NR = math.ceil(file_stats / 1024)         # Returns ceiling of filesize divided by 1024
        print('Number of Receives is ' + str(NR)) # Prints number of packets to send
        return str(NR)
    
    elif func == 'send':
        userFile = open(file, 'rb')            # Opens image in binary 
        data = userFile.read(1024)                 # Reads file in units of 1024 bytes
        while(data):
            clientSocket.sendto(data,(serverName, serverPort))
            data = userFile.read(1024)
            time.sleep(0.02)
        clientSocket.close()
        return

number_receives = Make_Packet(fileName, 'div').encode('utf8')
clientSocket.sendto(number_receives,(serverName, serverPort))    # Sends number to server
Make_Packet(fileName, 'send')