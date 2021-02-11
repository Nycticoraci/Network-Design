from socket import *
import time
import os
import math
serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
fileName = input(str("Hello friend! What is the name of the file?"))


file_stats = os.stat(fileName)#gets file information
NR = math.ceil(file_stats.st_size / 1024) #takes number /1024, rounds down
number_receives = bytes(NR) #converts number to bytes
print(f'Number of Receives is {NR}')


userFile = open(fileName, 'rb')
data = userFile.read(1024)
clientSocket.sendto(number_receives,(serverName, serverPort))#sends number to server
while (data):
    clientSocket.sendto(data,(serverName, serverPort))
    data = userFile.read(1024)
    time.sleep(0.02)
clientSocket.close()
