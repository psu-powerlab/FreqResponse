# Midrar Adham
# June-24-2020
# This file is meant to control NHR 9410 (Grid Simulator) frequency via SCPI Commands.
# An array of different values is used to accomplish this task.
# The equipment accepts values between 30-880 Hz.(Accodring to NHR 9400 Series AC/DC Power Module Programmer’s Reference Manual)
# For each command below, a brief description is provided.
# This file is available to anyone who would like to use it. Feel free to copy,edit, and develop its content.

# As you read through this file, you'll find flags. These flags are not important. They were used just for learning purposes.

# Here the code begins:
import csv
import socket                   #Import libraries
import time
import os

os.nice(-20)

def conn():
    global s
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(1000)
    s.connect(('192.168.0.149',5025))                               # NHR 9410 IP address
    output = 'SYST:RWL\n'                                           # Lock out the touch panel screen (Safety purposes)
    s.send(output.encode('utf-8'))                                  # Each SCPI command MUST be encoded into utf-8.
    return s
def clos(s):                                                        # This function is meant to close the connection
    output5 = 'SYST:LOC\n'                                          # Unlock the touch panel screen
    s.send(output5.encode('utf-8'))
    s.close()                                                       # Close the connection



def Gs():

    arr = []                                                        # Create an empty array
    with open("Aug_25.csv") as csv_file:                            # Open desired csv file
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        for rows in csv_reader:         
            y = rows['STATION_1:Freq']                              # Name of the desired column
            arr.append(float(y)+0.00723651)                         # Append frequency values in "Aug_25.csv" files into the empty array above (0.00724651 is an offset)

    conn()
    # s.send('FREQ 60.00 \n'.encode('utf-8'))                       # This command sets the NHR-9410 (GS) frequency to 60Hz. (You're welcome to uncommented and try it!)
    s.send('MACR:LEAR 1 \n'.encode('utf-8'))                        # This command changes the GS settings (Learning mode)
    s.send('MACR:OPER:SYNC:INST1 SYNC \n'.encode('utf-8'))          # This commands requests the GS to change frequency value each cycle (1 cycle = 1/60Hz)
    s.send('MACR:LEAR 0 \n'.encode('utf-8'))                        # Stop the learning process (No more modifications in the GS settings)
    s.send('MACR:RUN \n'.encode('utf-8'))                           # Set the previous settings    
    # The next block of the code is meant to send each frequency value that was read from "Aug_25.csv" file to the GS. (Take a look at the file!!)
    # Each command that is going to be sent goes through different network components (router,switch,etc). These components takes time to process each command. Hence, delay occurs.
    # Furthermore, the GS has two processors. The first one is used to translate the SCPI commands. The second one is used to execute the translated commands.
    # As more commands are sent to the GS, its processors take more time to execute the commands. Hence, time delay (x) is changed everytime.
    # After multiple testing processes, we figured out that the time delay (x) SHOULD be refreshed after 500 values.
    # You are MORE THAN WELCOME to try different approaches. If your approach works, YOU ARE A CHAMPION!
    output2 = 'FREQ '
    liss = []
    freq_val = []
    p = 0
    for i in arr:
        if 0 <= p <= 500:
            x = 0.0550
        if 501 <= p <=1000:
            x = 0.0280
        if 1001 <= p <= 1500: 
            x = 0.0290
        if 1501 <= p <= 2000:
            x = 0.0285
        if 2001 <= p <= 2500:
            x = 0.0295
        if 2501 <= p <= 3000:
            x = 0.0288
        if 3001 <= p <= 3500:
            x = 0.0288
        if 3501 <= p <= 4000:
            x = 0.0258
        if 4001 <= p <= 4500:
            x = 0.0285
        if 4501 <= p <= 5000:
            x = 0.0285
        if 5001 <= p <= 5500:
            x = 0.0285
        if 5501 <= p <= 6000:
            x = 0.0285
        if 6001 <= p <= 6500:
            x = 0.0285
        if 6501 <= p <= 7000:
            x = 0.0285
        if 7001 <= p <= 7500:
            x = 0.0285
        if 7501 <= p <= 8000:
            x = 0.0285
        if 8001 <= p <= 8500:
            x = 0.0285
        if 8501 <= p <= 9000:
            x = 0.0285
        if 9001 <= p <= 9500:
            x = 0.0285
        if 9501 <= p <= 10000:
            x = 0.0285
        if 10001 <= p <= 10500:
            x = 0.0285
        if 10501 <= p <= 11000:
            x = 0.0285
        if 11001 <= p <= 11500:
            x = 0.0285
        if 11501 <= p <= 12000:
            x = 0.0285
        if 12001 <= p <= 12500:
            x = 0.0290
        if 12501 <= p <= 13000:
            x = 0.0290
        if 13001 <= p <= 13501:
            x = 0.0290
        if 13501 <= p <= 14000:
            x = 0.0290
        if 14001 <= p <= 14500:
            x = 0.0290
        if 14501 <= p <= 15000:
            x = 0.0290
        if 15001 <= p <= 15500:
            x = 0.0290
        if 15501 <= p <= 16000:
            x = 0.0290
        if 16001 <= p <= 16500:
            x = 0.0290
        if 16501 <= p <= 17000:
            x = 0.0290
        if 17001 <= p <= 17500:
            x = 0.0290
        if 17501 <+ p <= 18000:
            x = 0.0290
            
            
        # The code block below is meant to restrict python compiler to the specified time delay (x).
        
        
        start_time = time.time()                                    # This command is to assign real time vlaue to variable "start_time"
        t_end = time.time() + x                                     # Here we added the above time delay (x) to "start_time" variable 
        while time.time() < t_end:                                  # Creating a delay loop
            k = 1                                                   # Meaningless! Just to give the compiler something to do while waiting!
        var = output2 + str(i)+'\n'                                 # Assign a SCPI command to a variable.
        s.send(var.encode('utf-8'))                                 # Encoding the SCPI command and send it
        end_time = time.time()                                      # This is for debugging purposes 
        diff = end_time - start_time                                # This is for debugging purposes
        diff_list = liss.append(diff)                               # This is for debugging purposes
        s.send('FREQ?\n'.encode('utf-8'))                           # This a query. (what is a query? Ask me if you don't know what a query is!) This commands is used to obtain the GS frequency value. 
        msg = s.recv(1024).decode()                                 # The GS will respond to the above query. The reponse must be decoded.
        freq_val.append(msg)
        p = p + 1

    return diff_list, freq_val, arr
    clos(s)
Gs()


