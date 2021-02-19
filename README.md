# Network-Design

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
