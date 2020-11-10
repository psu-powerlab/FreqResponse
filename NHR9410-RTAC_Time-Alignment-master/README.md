# NHR9410-RTAC_Time-Alignment

## Credits:

Thanks to Dr. Robert Bass, Sean Keene, and Mohammed Alsaid for their ultimate support.

## Purpose:

This project to meant to time-align NHR 9410 (Grid Simulator) and Real-Time Automation Controller (RTAC), perform calibration and testing procedures.

## Location:

The Grid Simulator and the RTAC reside at Portland State University, ECE Department, PowerLab. 

## Equipement:

NHR 9410 regenrative Grid Simulator https://nhresearch.com/power-electronics-test-systems-and-instruments/ac-dc-regenerative-loads/regenerative-grid-simulator-model-9410/

SEL RTAC https://selinc.com/products/3530/

## Procedure:

###### Before starting the procedure, email me at midrar@pdx.edu to provide you with the needed credentials. You will need the following:

1. confirm GS setup.
2. Linux credentials (IP address, username and password).
3. "Remote" computer credentials.
4. PowerLab_GS credentials

The tesing was done on four computers due to COVID-19 pandemic, three of which are located in PowerLab. The steps below should help my fellow students and researchers to perform an adequate testing procedure.

###### Setting up the GS:
1. **Send an email to (Midrar@pdx.edu) for permission.**
2. **DO NOT PROCEED UNTIL YOU GET A CONFIRMATION EMAIL!!**
###### Setting up the server:
1. Open up command prompt or terminal on your computer.
2. ssh username@IP_Address
3. Change directory to /home/deras/Desktop/Gs/midrar by typing: cd /home/deras/Desktop/Gs/midrar
4. Run the server by typing: sudo python3 serv.py
5. It will ask you for a password. Use the password given in the email above.
6. Server is up. Now let's set the client.
###### Setting up the RTAC:
1. Login into "Remote" computer.
2. You should find SEL AcSELerator RTAC interface opened.
3. On the left bar of SEL AcSELerator RTAC interface, you should find LabTestRecorder. Click on it.
4. Click on LabTestRecorder tab.
5. Adjust "Enable Recorder" to "True". It is case sensitive.
6. Go back to the search bar and type WinSCP. (It should be already opened!)
7. WinSCP has two windows. On the right window, right click > Static Custome Commands > Keep Local Directory up to Date.
8. In "Watch for changes in the remote directory", choose "/FILES/LabTestRecording/"
9. In "...and automatically reflect them on the local directory:", choose "G:\My Drive\PGE Frequency Response\midrar_files_2"
10. In the "Interval (in secodns)" bar, type 0.1
11. PowerShell should open. This PowerShell is checking for files in the specified directory every 0.1 seconds.
12. Now open command prompt and type the following "cd \Users\Remote\Desktop\Midrar_Files" .This will change directory (cd) to C:\Users\Remote\Desktop\Midrar_Files
13. In the command prompt, type python3 "test.py" . This will set up client and connect to the server above.
14. Now once the directory G:\My Drive\PGE Frequency Response\midrar_files_2 gets a new file, the client will send a ping to the server and turn off. The server will run the python file that has the frequency event and waits for another ping. The RTAC will execute a csv file every 10 minutes.
15. Once a csv file is written in the directory specified, you can download it to the drive by clicking onto the "Download" tab on the WinSCP and choose "Download and Delete" option.
16. Go to the drive and download the csv file to your computer. The new csv file should in this directory on the drive PGE Frequency Response\midrar_files_2.
17. Now use the file in this repository "practice.py". Change the name of the csv file to the name of the file that you just downloaded from the drive.
18. Run the python code. Done!
