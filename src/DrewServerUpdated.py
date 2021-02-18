import sys
from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print('The server is ready to receive')

while True:
    number_receives, clientAddress = serverSocket.recvfrom(1024)      # Receive number of receives from client
    myNewFile = open('output.jpg', 'wb')
    number_receives = str(number_receives, 'utf8')
    print('Number of Receives: ' + number_receives)                   # Prints to confirm the number was successfully received

    for receive in range(int(number_receives)):                    # Rewrites the image one packet at a time
        message, clientAddress = serverSocket.recvfrom(1024)       # per the number of packets received as
        if not message:                                            # given by "number_receives"
            break
        else:
            myNewFile.write(message)
            # I added an increment here to keep track of where in the process the script is
            print('Got it! Thanks [' + str(receive + 1) + '/' + str(number_receives) + ']')
    
myNewFile.close()
serverSocket.close()