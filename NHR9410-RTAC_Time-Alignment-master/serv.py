# This file is used to create a server. Refer to the README.md file to understand the purpose of this file.
# This file SHALL be ran with "sudo" prior the "python3 F-Resp-csv_MACRo.py" in terminal.(If you're using windows, run command prompt with administrative Credentials)


import socket
import os
import time

s = socket.socket()
s.settimeout(1000)
s.bind(('',9991))
s.listen(5)
print('server is up!')

print(os.getpid())
while True:
    c,a = s.accept()
    d = c.recv(1024)
    print(d)
    if (d.decode('utf-8') == 'ping'):
        os.system('python3 F-Resp-csv_MACRo.py')
    if not d:
        break
 
