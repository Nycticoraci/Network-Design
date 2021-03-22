from socket import *
import time
import os
import subprocess
import math
import tkinter as tk
from tkinter import simpledialog

serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Creates simple popup GUI
root = tk.Tk()
root.withdraw()
fileName = simpledialog.askstring(title = 'Client Input',
                                  prompt = 'Hello friend! What is the path for your file?')

# Creates a list where each index holds 1024 bytes of the image file
# in sequential order
def Make_Packet(packet, data):
    packet_list = []
    userFile = open(data, 'rb')
    packet_size = userFile.read(1024)
    for i in range(packet):
        packet_list.append(packet_size)
        packet_size = userFile.read(1024)
    return packet_list

outputName = fileName
linux = subprocess.run(['uname'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#print(linux.returncode)
if linux.returncode == 0:
    i = outputName.rfind('/')                               #If uname completes successfully (return code 0), linux env is true
else:                                                       #else run path for windows
    i = outputName.rfind('\\')                              #Get the last path index
#print(i)                                                   #Check the index of the last path (file name)
print('File name is: '+ outputName[i+1:])                   #Verify user input is correct
print('File path is: '+ fileName)
outputName = outputName[i+1:].encode('utf8')                #Encode file name
clientSocket.sendto(outputName,(serverName, serverPort))    #Send file name to server
time.sleep(0.02)                             # Pause the process so that the server does not mix up the packets for file name and fize size
file_size = os.stat(fileName).st_size        # Gets size of the file in bytes
NR = str(math.ceil(file_size / 1024))        # Returns ceiling of filesize divided by 1024
print('Number of Receives is ' + NR)         # Prints number of packets to send
number_receives = NR.encode('utf8')
clientSocket.sendto(number_receives,(serverName, serverPort))    # Sends number to server

# Sends Make_Packet() the # of divisions to make, as well
# as the file to divide
rdt_send = Make_Packet(int(NR), fileName)

# Sends each 1024 byte division of the image file in order
for packet in rdt_send:
    clientSocket.sendto(packet,(serverName, serverPort))
    time.sleep(0.02)
clientSocket.close()
