import sys
from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("The server is ready to receive")
myNewFile = open('output.jpg','wb')

number_receives, clientAddress = serverSocket.recvfrom(1024)   # Receive number of receives from client
number_receives = str(number_receives, 'utf8')
print('Number of Receives: ' + number_receives)                # Prints to confirm the number was successfully received

for receive in range(int(number_receives)):                    # Rewrites the image one packet at a time
    message, clientAddress = serverSocket.recvfrom(1024)       # per the number of packets received as
    if not message:                                            # given by "number_receives"
        break
    else:
        myNewFile.write(message)
        print("Got it! Thanks")
    
myNewFile.close()
serverSocket.close()