# Phase Two Design Doc
Network Design
2/21/2021

### Authors
1. Jaki Giggi
2. Jack Flood
3. Tyler Almachar
4. Drew Bowler

### Purpose of the Phase
The purpose of this phase is to send and receive a file of at least 500 KB through UDP sockets in python. 

### Code Explanation
Client Side
1. Declare server hostname & port
2. Initialize socket
3. Start pop-up gui with tkinter
4. Prompt user to enter file path
5. Definition: Make_Packet
  5a. Initialize array
  5b. Open user file, read data in
  5c. For i in range packet, create packets of 1024b and insert into array
  5d. Return array of packets (packet list)
6. Isolate file name from user input
  6a. send file name to server
7. Send number of receives to server
8. Send packets to server
9. Close socket

Server Side
1. Declare server hostname & port
2. Initialize socket
3. While true, 
  3a. Print 'server is ready'
  3b. Receive file name from client, convert to utf8
  3c. Open file, write-enabled
  3d. Receive packet list from client, convert tot utf8
  3e. Print file name and packet count
  3f. For number of receives, write to output file
  3g. Print '% received/ total # packets' to command line
4. Close output file
5. Close server socket

### Execution Example

