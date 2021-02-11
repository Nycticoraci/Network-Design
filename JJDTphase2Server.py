import sys

from socket import *
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print("The server is ready to receive")
myNewFile = open("output.jpg",'wb')
a=0 #counter variable
number_receives, clientAddress = serverSocket.recvfrom(1024) #receive number of receives

print(f'Number of Receives {number_receives}') #prints to confirm operational
while True:
    message, clientAddress = serverSocket.recvfrom(1024)
    if not message:
        break
    else:
        myNewFile.write(message)
    print("Got it! Thanks")
    a += 1; #counts number of receives
    
    if a == number_receives:
        break
myNewFile.close()
serverSocket.close()

