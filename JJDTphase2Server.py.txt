from socket import *
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print("The server is ready to receive")
myNewFile = open("output.jpg",'wb')
while True:
    message, clientAddress = serverSocket.recvfrom(1024)
    if not message:
        break
    else:
        myNewFile.write(message)
    print("Got it! Thanks")
myNewFile.close()
serverSocket.close()