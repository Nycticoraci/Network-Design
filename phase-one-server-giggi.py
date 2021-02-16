#Jaki Giggi
#2/8/2021
#Network Design Project
#Phase One

#import socket library
from socket import *

#define ports, server address, and socket type
serverPort              = 12000
server                  = socket(AF_INET, SOCK_DGRAM)
server.bind(('localhost', serverPort))

#let the user know the server is ready
print('Server is ready to receive')

#host is 'always-on' and ready to receive
while(1):
    #receive message from client
    message, clientAddr = server.recvfrom(2048)
    #show user the message that's been received
    print('Received: '+str(message.decode()))

    #modify user's message in a known pattern to verify receipt
    modMessage = message.decode().upper()
    #show user the message that should be received on the client
    print('Sending: '+str(modMessage))
    #send message to client
    server.sendto(modMessage.encode(), clientAddr)
#close socket
server.close()
################################################################################
