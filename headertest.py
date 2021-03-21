seqNum = str(1)
checkSum = 0x1A52
data = 0x0F0F0F0F

binSeq = int(seqNum, base=16)
binSeq = format(binSeq, '#04b')[2:]
print("Sequence Number: " + binSeq)

binCheck = format(checkSum, '#018b')[2:]
print("CheckSum:         ", binCheck)

binData = format(data, '#034b')[2:]
print("Data:                              " + binData)

datagram = binSeq + binCheck + binData
print("Datagram:       ", datagram)
