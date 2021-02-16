#Jaki Giggi
#2/8/2021
#Network Design Project
#Phase One

#import socket library
from socket import *

#define host connections, socket type, and message to be delivered
server                  = 'localhost'
serverPort              = 12000
client                  = socket(AF_INET, SOCK_DGRAM)
message                 = 'hello socket'

#send message to server
client.sendto(message.encode(), (server, serverPort))
#receive receipt from server
modMessage, serverAddr  = client.recvfrom(2048)
#show user the server's response
print (str(modMessage.decode()))
#close socket
client.close()
##################################################################################
