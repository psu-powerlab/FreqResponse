# This file is used to create a client. Refer to the README.md file to understand the purpose of this file.
import socket
import os
import time

# print('PID: ',os.getpid())
s = socket.socket()
# s.connect(('131.252.218.84',9991))
s.connect(('10.218.219.90',9991))
path = "G:/My Drive/PGE Frequency Response/midrar_files_2"		
lis = os.listdir(path)
length = len(lis)

while True:
	lis1 = os.listdir(path)
	length1 = len(lis1)
	if (length) < (length1):
		s.send('ping'.encode())
		print(time.time())
		exit()
