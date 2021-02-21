# Phase Two ReadMe

### Team Members:
1. Jaki Giggi
2. Jack Flood
3. Drew Bowler
4. Tyler Almachar 

### Environment
  Operating System: Windows
  Language: Python v3.9.1

### Instructions
1. Download files
2. Open two CMD or bash shells, navigate to file location if necessary
3. Start the server: 
    ex. python phase2_server.py
5. Start the client:
    ex. python phase2_client.py
7. Enter the path to your file into the window prompt 
    ex. C:\Users\jacqu\OneDrive\Network Design\jadzia.bmp
8. Hit enter
9. Check file destination (where the python source files are)

### Other Notes

Sending side:
1. Accept the data to be sent
2. Send the data to Make_Packet() to be cut into chunks of 1024 bytes
3. Send the chunks from Make_Packet to the server

Receiving side:
1. Collect the sent data
2. Assemble it (by writing to an open file)
3. Output the final image by saving the completed file

--------------------------------
Potential shortcomings:
Sending side: I'm not sure if it's correct to have Make_Packet() cut up the file into chunks
all at once, or if it's supposed to send it as soon as it's been cut up. That's
what the code did before we had Make_Packet(), but then it doesn't require a new
function at all.

Receiving side: I'm not sure if the receiving side needs more defined functions, or
if it follows the RDT1.0 flow chart in execution. The fact it works at all makes me
think it does... but I'm not 100% sure.
