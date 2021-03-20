seqNum = str(1)
checkSum = 0x1A52
data = 0x0F0F0F0F

binSeq = int(seqNum, base=16)
binSeq = format(binSeq, '#04b')
binSeq = '{:<052}'.format(binSeq)
print("Sequence Number: " + binSeq)

binCheck = format(checkSum, '#018b')
binCheck = '{:<050}'.format(binCheck)
print("CheckSum:          " + binCheck)

binData = format(data, '#034b')
print("Data:                              " + binData)

#datagram = int((binSeq),base=16) + int((binCheck),base=16) + int((binData),base=16)
#datagram = format(datagram, '#052b')
#print("Datagram: ", datagram)