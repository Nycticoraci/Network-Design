from socket import *
import time
serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
fileName = input(str("Hello friend! What is the name of the file?"))
userFile = open(fileName, 'rb')
data = userFile.read(1024)
while (data):
    clientSocket.sendto(data,(serverName, serverPort))
    data = userFile.read(1024)
    time.sleep(0.02)
clientSocket.close()
