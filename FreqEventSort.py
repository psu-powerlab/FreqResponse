# -*- coding: utf-8 -*-
"""
This is the event processing and plotting program for F-RESP. I NEED TO RENAME
IT.

7/8/2020 This doesn't count as a "release" but I'm putting it up to get back
in the habit of using GitHub. I expect to do a full rewrite at the end of 
summer, so this program in this form isn't representative. 

Written by Sean Keene w/ contributions by Noah Johansen
7/8/2020

"""

import ftplib
import csv
import os
from ftplib import FTP
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import pandas as pd
import numpy as np
import datetime as dt
import dateutil
from dateutil.parser import parse
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.widgets import Button
import matplotlib.pyplot as plt
import re

#--Initialization--
#   The program needs to be connected to the FTP on startup.
ftp = FTP('192.168.1.2')
ftp.login('admin', 'TAIL')
ftp.cwd('FILES/Recording')
# This apparently is a keep-alive option for the FTP.
# ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

global DL_COUNT
DL_COUNT = 0



class Event:
    """A catchall object containing a single .csv event file's metadata and
        some processing methods. process_event is the biggest method and should
        honestly have a class for itself."""

    def __init__(self):
        
        #This dictionary contains all the metadata for a single file. A dict
        #is used because it's easy to read and trivial to write to file.
                self.metadict = {
                        'archive_index_number': int(),
                        'timestamp': dt.datetime(1970, 1, 1),
                        'non_event_flag': False,
                        'over_freq_flag': False,
                        'over_freq_index': np.nan,
                        'under_freq_flag': False,
                        'under_freq_index': np.nan,
                        'ambig_flag': False,
                        'severity_desc': 'None',  # Based on Slew Rate
                        'file_name': '',
                        'ABC_values': [np.nan, np.nan, np.nan]
                        }

    def process_event(self, file_path, archive_index):
        """Preloads an Event's dictionary for future sorting.
            Designed for both initial sorting and archive repair.
            A jumbled mess, as it fulfils both data processing into the
            metadict as well as corrective actions that should be handled
            by a designated process, but are instead shoved into exception 
            handlers on the fly. 
        """

        self.metadict['file_name'] = file_path
        print(self.metadict)
        try:
            #Attempts to read the csv into a dataframe. dtype is used to 
            #detect the garbage character issue.
            init_table = pd.read_csv(self.metadict['file_name'],
                                     encoding='latin_1',
                                     dtype={'STATION_1:SlewRate': "float64"})
        except (ValueError, TypeError):
            #If an unexpected character is in an entry in the SlewRate column,
            #this handler will catch it and use a regular expression to remove
            #all unexpected data, retain the actual values, and force the
            #column back into a float.
            print('Data Type Error, Fixing...')
            try:
                init_table = pd.read_csv(self.metadict['file_name'],
                                         encoding='iso-8859-1')



                init_table['STATION_1:SlewRate'].replace(regex=True,
                                                         inplace=True,
                                                         to_replace=r'[^0-9.\-E]',
                                                         value=r'')
                init_table['STATION_1:SlewRate'] = init_table['STATION_1:SlewRate'].astype('float64')
            except ValueError:
                #If there is a '#NaN' in the data, this handler detects it and
                #moves the file to a quarantine folder.
                print("NAN file, quarantining...")
                fn = file_path.replace(ARCHIVEPATH, '')
                quarpath = "G:/My Drive/PGE Frequency Response/NAN Quarantine/"
                os.replace(file_path, quarpath + fn)
                pass
            try:
                #Write repaired dataframe to the original file.
                init_table.to_csv(file_path, index=False)

                # init_freq_list = init_table['STATION_1:Freq']

                init_time_list = init_table['Timestamp']
                try:
                    #Create an array with the timestamps for the file
                    init_datetime = parse(init_time_list[0])
                except dateutil.parser._parser.ParserError:
                    #Fixes the weird first line data issue. 
                    with open(self.metadict['file_name'], 'r+') as timecode_row_fixer:
                        f = timecode_row_fixer.readline()
                        print(f)
                        g = timecode_row_fixer.readline()
                        print(g)
                        p = re.finditer(r'[0-9]{4}\/[0-9]{2}\/[0-9]{2}', g)
                        #testout = p.match(g)
                        for match in p:
                            span_tuple = match.span()
                        new_g = g[span_tuple[0]:]
                        print(new_g)
                        rest_of_file = timecode_row_fixer.read()
                        #NOTE: PROBABLY DO SOMETHING ELSE THAN A BUNCH OF SPACES
                        bunch_of_spaces = '                                                                                                                                                                                  '
                        full_new_file = f+new_g+rest_of_file+bunch_of_spaces
                        timecode_row_fixer.seek(0, 0)
                        timecode_row_fixer.write(full_new_file)
                        print(full_new_file)
                    init_table = pd.read_csv(self.metadict['file_name'],
                                             encoding='iso-8859-1')
                    init_time_list = init_table['Timestamp']
                    init_datetime = parse(init_time_list[0])

                    # init_table.drop(init_table.index[[0]], inplace=True)
                            # init_time_list = init_table['Timestamp']
                            # init_datetime = parse(init_time_list[0])
                    pass

                #Use timestamp table to add a "start time" to metadict
                self.metadict['timestamp'] = init_datetime
                print(self.metadict['timestamp'])

                # The following use exception handlers to automate an if/then
                # condition for each OF/UF flag. This allows us to describe 
                # each event in the metadata for later sorting.
                init_ofdetect_list = init_table['STATION_1:OFDetect'].tolist()
                try:
                    self.metadict['over_freq_index'] = init_ofdetect_list.index(1)
                    self.metadict['over_freq_flag'] = True
                    self.metadict['severity_desc'] = 'Minor'
                except ValueError:
                    self.metadict['over_freq_index'] = np.nan
                    self.metadict['over_freq_flag'] = False
                    self.metadict['severity_desc'] = 'None'

                init_ufdetect_list = init_table['STATION_1:UFDetect'].tolist()
                try:
                    self.metadict['under_freq_index'] = init_ufdetect_list.index(1)
                    self.metadict['under_freq_flag'] = True
                    self.metadict['severity_desc'] = 'Minor'
                except ValueError:
                    self.metadict['under_freq_index'] = np.nan
                    self.metadict['under_freq_flag'] = False
                    self.metadict['severity_desc'] = 'None'

                try:
                    init_ofslew_list = init_table['STATION_1:OFSlew'].tolist()
                except KeyError:
                    # I don't actually remember what this is for. Some error.
                    print('Slew Rate KeyError')
                    init_table['STATION_1:SlewRate'] = pd.to_numeric(init_table['STATION_1:SlewRate'], errors='coerce')
                    repair_slewrate_list = init_table['STATION_1:SlewRate'].tolist()
                    repair_of_flag_list = [i >= 0.003 for i in repair_slewrate_list]
                    repair_uf_flag_list = [i <= -0.003 for i in repair_slewrate_list]
                    init_table['STATION_1:OFSlew'] = repair_of_flag_list
                    init_table['STATION_1:UFSlew'] = repair_uf_flag_list
                    init_table.to_csv(self.metadict['file_name'])
                    init_ofslew_list = init_table['STATION_1:OFSlew'].tolist()
                try:
                    init_ofslew_list.index(1)
                    self.metadict['severity_desc'] = 'Major'
                except ValueError:
                    pass

                init_ufslew_list = init_table['STATION_1:UFSlew'].tolist()
                try:
                    init_ufslew_list.index(1)
                    self.metadict['severity_desc'] = 'Major'
                except ValueError:
                    pass

                if (self.metadict['under_freq_flag']
                        + self.metadict['over_freq_flag'] == 2):
                    self.metadict['ambig_flag'] = True
                else:
                    self.metadict['ambig_flag'] = False

                self.metadict['archive_index_number'] = archive_index
            except UnboundLocalError:
                #Another #NaN catcher.
                try:
                    #ALSO MOVE TO QUARATINE IF FAILED TO LOAD TABLE
                    print("NAN file + badtime error, quarantining...")
                    fn = file_path.replace(ARCHIVEPATH, '')
                    quarpath = "G:/My Drive/PGE Frequency Response/NAN Quarantine/"
                    os.replace(file_path, quarpath + fn)
                    pass
                except FileNotFoundError:
                    print("Already Quarantined. Pass.")
                    pass
                
    def write_eventlog(self):
        """Writes the metadict to a line of the metadata file."""
        global filename
        csv_columns = list(self.metadict.keys())
        csv_file = filename  # TODO: change
        try:
            with open(csv_file, 'a') as csvfile:
                writer = csv.DictWriter(csvfile, lineterminator='\n',
                                        fieldnames=csv_columns)
#                writer.writeheader()
                writer.writerow(self.metadict)

        except IOError:
            print("I/O error")

    def read_file_name(self, filename):
        self.metadict['file_name'] = filename

    def abc_calc(self):
        pass

class CustomToolbar(NavigationToolbar2Tk):
    """custom toolbar with lorem ipsum text NOTE: Noah work. I don't know what
        this is yet."""

    def __init__(self, canvas_, parent_):
        self.toolitems = (
            ('Subplots', 'putamus parum claram', 'subplots', 'configure_subplots'),
            ('Save', 'sollemnes in futurum', 'filesave', 'save_figure'),
            (None,None,None,None)
            )
        NavigationToolbar2Tk.__init__(self, canvas_, parent_)


def connect_to_ftp():
    """Creates an FTP object with the proper username, password, and path."""

    ftp = FTP('192.168.1.2')
    ftp.login('admin', 'TAIL')
    ftp.cwd('FILES/Recording')


def process_one_file(i):
    """Copies a file from the ftp, runs event processing, and deletes
    the redundant file from the FTP"""

    stream_statustxt.configure(text="Now Processing: " + i)
    file_path = ARCHIVEPATH + '/' + i
    localfile = open(file_path, 'wb')
    ftp.retrbinary('RETR '+i, localfile.write, 1024)
    localfile.close()
    new_index = int(Current_Event.metadict['archive_index_number']) + 1
    Current_Event.process_event(file_path, new_index)
    filesize_after_download = os.path.getsize(file_path)
    #"Fix" for the 0kb filesize error. Unused since it seems to be RTAC side
    if (filesize_after_download < 100):
        raise Exception("Warning: File became small after transfer. Troubleshoot me.")
    else:
        ftp.delete(i)
    global DL_COUNT
    DL_COUNT = DL_COUNT + 1
    label_counter.configure(text=str(DL_COUNT) +
                            ' files downloaded this session')
    stream_statustxt.update()
    Current_Event.write_eventlog()


def read_archive_line(line_num):
    """Opens the archive metadata csv, reads a single line, RETURNS THE
    DICTIONARY, and then closes the archive."""
    global filename
    csv_file = filename
    try:
        with open(csv_file, 'r') as csvfile:
            csvRowArray = []
            for row in csv.DictReader(csvfile):
                csvRowArray.append(row)
        return dict(csvRowArray[line_num])
    except IOError:
        print("I/O error")


def update_archive():
    """Completely reprocess the archive as though it were being streamed for
    the first time. Takes a very long time due to the Google Drive
    download/sync speed bottleneck. Use only during major updates that
    effect the base metadictionary!"""

    new_archive = 'newarchive.csv'
    Load_Event = Event()
    new_archive_columns = list(Load_Event.metadict.keys())
    archive_index_number = 0
    with open(new_archive, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, lineterminator='\n',
                                fieldnames=new_archive_columns)
        archive_file_list = os.listdir(ARCHIVEPATH)
        archive_file_list.sort()
        writer.writeheader()
        for i in archive_file_list:
            file_path = ARCHIVEPATH+'/'+i
            try:
                Load_Event.process_event(file_path, 0)
                Load_Event.metadict['archive_index_number'] = archive_index_number
                archive_index_number = archive_index_number + 1
                writer.writerow(Load_Event.metadict)
            except pd.errors.EmptyDataError:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print("File Removed")
                else:
                    print("The file does not exist")
            except pd.errors.ParserError:
                    print("Parser Error. Verify desktop.ini to confirm Archive rebuild complete")



def start_stream():
    """Begins file transfer stream from FTP to the preset download folder.
    Also contains exception handler for FTP kickoff situations.
    If FTP connects, runs process_one_file() for all detected files."""

    listbutton.configure(text="Streaming files...")
    try:
        linelist = ftp.nlst()
        for i in linelist:
            filesize_on_ftp = ftp.size(i)
            if (filesize_on_ftp < 100): #Assists in troubleshooting 0kb file issue
                raise Exception("Error: Filesize on FTP too small.")
            else:
                process_one_file(i)
        stream_statustxt.after(60000, start_stream)
    except AttributeError as e:
        print(e)
        print('Attempting to reconnect to FTP (1)')
        try:
            ftp.quit()
            connect_to_ftp()
            linelist = ftp.nlst()
            for i in linelist:
                process_one_file(i)
            stream_statustxt.after(60000, start_stream)
        except Exception as e:
            print(e)
            print('Reconnection Failed. (1)')
            ftp.quit()
            listbutton.configure(text="Begin FTP Stream")
    except ftplib.all_errors as e:
        print(e)
        print('Attempting to reconnect to FTP (2)')
        try:
            ftp.quit()
            connect_to_ftp()
            linelist = ftp.nlst()
            for i in linelist:
                process_one_file(i)
                Current_Event.write_eventlog()
            stream_statustxt.after(60000, start_stream)
        except Exception as e:
            print(e)
            print('Reconnection Failed. (2)')
            ftp.quit()
            listbutton.configure(text="Begin FTP Stream")


def update_archive_tree():
    """Updates the archive treeview (for plot selection). NOTE: Is this used?
    Check and see if Noah modified. the hardcoded csv_file seems off."""
    Tree_Event = Event()
    csv_file =  "test.csv"  # TODO: change
    try:
        with open(csv_file, 'r') as csvfile:
            for row in csv.DictReader(csvfile):
                Tree_Event.metadict.update(dict(row))
                tree.insert("", "end",
                            text=Tree_Event.metadict['archive_index_number'],
                            values=(Tree_Event.metadict['timestamp'],
                                    Tree_Event.metadict['over_freq_flag'],
                                    Tree_Event.metadict['under_freq_flag'],
                                    Tree_Event.metadict['ambig_flag'],
                                    Tree_Event.metadict['severity_desc']))
    except IOError:
        print("I/O error")


def test_button():
    print(tree.item(tree.focus())['text'])
    

# # def tree_plot():
    
# #     try:
# #         Plot_Event = Event()
# #         Plot_Event.metadict.update(read_archive_line(int(tree.item(tree.focus())['text'])))
# #         plot_table = pd.read_csv(Plot_Event.metadict['file_name'], dtype={'STATION_1:SlewRate' : "float64"})
# #         freq_xaxis = np.linspace(0, 18000, 18000)
# #         freq_yaxis = plot_table['STATION_1:Freq']
# #         plot_freq = figure(plot_width=1800, plot_height=400,
# #                            title=Plot_Event.metadict['timestamp'],
# #                            x_axis_label='Time in frames',
# #                            y_axis_label='Frequency (Hz)',
# #                            tooltips=[("index", "$index"),
# #                                      ("Frequency", "$y")])
# #         plot_freq.line(freq_xaxis, freq_yaxis,
# #                        legend="Frequency", line_width=1)
# #         slew_xaxis = np.linspace(0, 18000, 18000)
# #         slew_yaxis = plot_table['STATION_1:SlewRate']
# #         plot_slew = figure(plot_width=1800, plot_height=400,
# #                            x_range=plot_freq.x_range,
# #                            title=Plot_Event.metadict['timestamp'],
# #                            x_axis_label='Time in frames',
# #                            y_axis_label='Slew Rate',
# #                            tooltips=[("index", "$index"),
# #                                      ("Slew", "$y")])
# #         plot_slew.line(slew_xaxis, slew_yaxis, legend="Slew Rate", line_width=1)
# #         plot_slew.line(slew_xaxis, 0)
        
#     except FileNotFoundError:
#         print('File not found.')




#---TK Window Stuff---
labelvar = "Test FTP Program"

root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
screen_resolution = str(screen_width)+'x'+str(screen_height)
root.geometry(screen_resolution)
root.title("F-RESP Archived Recording Tool")
tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab4 = ttk.Frame(tab_control)

tab_control.add(tab1, text="Main Menu")
tab_control.add(tab2, text="File Tree")
tab_control.add(tab3, text="Options")
tab_control.add(tab4, text="Plot")
tab_control.pack(expand=1, fill="both")


stream_statustxt = tk.Label(tab1, text=labelvar)
stream_statustxt.pack()
listbutton = tk.Button(tab1,
                       text="Begin FTP stream",
                       command=start_stream)
listbutton.pack()
label_counter = tk.Label(tab1,
                         text=str(DL_COUNT) + ' files downloaded this session')
label_counter.pack()


tree = ttk.Treeview(tab2)
tree['columns'] = ('datetime', 'of', 'uf', 'ambig', 'severity')
tree.heading('#0', text='#')
tree.column('#0', minwidth=0, width=100)
tree.heading('datetime', text='Start Time')
tree.heading('of', text='Overfrequency')
tree.heading('uf', text='Underfrequency')
tree.heading('ambig', text='Ambiguous')
tree.heading('severity', text='Severity')
tree.pack(side='left')
scrollbar = ttk.Scrollbar(tab2, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side='right', fill='y')
refreshbutton = tk.Button(tab2, text="Refresh Tree", command=update_archive_tree)
refreshbutton.pack()
itemtestbutton = tk.Button(tab2, text="Test", command=test_button)
itemtestbutton.pack()
# ploteventbutton = tk.Button(tab2, text="Plot Selected Event", command=tree_plot)
# ploteventbutton.pack()
archive_remake_button = tk.Button(tab3,
                                  text="Remake Archive (!Turn off FTP!!)",
                                  command=update_archive)
archive_remake_button.pack()

# ARCHIVEPATH and csv file is now configurable by the user at runtime
# TODO: User selection by an OPTIONS menu. 
filename = filedialog.askopenfilename(filetypes = (("CSV File", "*.csv"),) )

ARCHIVEPATH = askdirectory()

# Initialize first event

Current_Event = Event()
Current_Event.metadict.update(read_archive_line(-1))
print(Current_Event.metadict)

# MATPLOTLIB port of Bokeh functionality. 
# Documentation for adding buttons for back/next functionality:
# https://matplotlib.org/3.1.0/gallery/widgets/buttons.html


def TrueEvent(index):
    """I have no idea."""
    global i
    global bnext, bprev, button
    global ax1, ax2, fig, canvas
    
    ax1.cla()
    ax2.cla()
    bnext.destroy()
    bprev.destroy()
    button.destroy()
    
    Plot_Event = Event()
    # provided that their lengths match
    df.loc[df.index[index], 'Event Check'] = True
    df.to_csv(filename)
    i = i+1    
    Current_Line = Plot_Event.metadict.update(read_archive_line(index+1))
    plot_table = pd.read_csv(Plot_Event.metadict['file_name'], dtype={'STATION_1:SlewRate' : "float64"})
    freq_yaxis = plot_table['STATION_1:Freq']
    slew_yaxis = plot_table['STATION_1:SlewRate']
    freq_xaxis = np.linspace(0, 18000, len(freq_yaxis))
    slew_xaxis = np.linspace(0, 18000, len(slew_yaxis))
    fig.suptitle(Plot_Event.metadict['timestamp'])
    ax1.plot(freq_xaxis, freq_yaxis)
    ax2.plot(slew_xaxis, slew_yaxis, 'tab:red')
    button = tk.Button(tab4, text="Quit", command=_quit)
    button.pack()
    bnext = tk.Button(tab4, text="True Event", command = lambda: TrueEvent(i+1))
    bnext.pack()
    bprev = tk.Button(tab4, text="False Event", command = lambda: FalseEvent(i+1))
    bprev.pack()
    canvas.draw()
    df.drop(columns='Unnamed: 0')
    print(index)
   
    

def FalseEvent(index):
    
    global i
    global bnext, bprev, button
    global ax1, ax2, fig, canvas
    
    ax1.cla()
    ax2.cla()
    bnext.destroy()
    bprev.destroy()
    button.destroy()
    
    Plot_Event = Event()
    # provided that their lengths match
    df.loc[df.index[index], 'Event Check'] = False
    df.to_csv(filename)
    i = i+1    
    Current_Line = Plot_Event.metadict.update(read_archive_line(index+1))
    plot_table = pd.read_csv(Plot_Event.metadict['file_name'], dtype={'STATION_1:SlewRate' : "float64"})
    freq_yaxis = plot_table['STATION_1:Freq']
    slew_yaxis = plot_table['STATION_1:SlewRate']
    freq_xaxis = np.linspace(0, 18000, len(freq_yaxis))
    slew_xaxis = np.linspace(0, 18000, len(slew_yaxis))
    
    fig.suptitle(Plot_Event.metadict['timestamp'])
    ax1.plot(freq_xaxis, freq_yaxis)
    ax2.plot(slew_xaxis, slew_yaxis, 'tab:red')
    button = tk.Button(tab4, text="Quit", command=_quit)
    button.pack()
    bnext = tk.Button(tab4, text="True Event", command = lambda: TrueEvent(i+1))
    bnext.pack()
    bprev = tk.Button(tab4, text="False Event", command = lambda: FalseEvent(i+1))
    bprev.pack()
    canvas.draw()
    df.drop(columns='Unnamed: 0')
    print(index)
    


Plot_Event = Event()
index = 1
i = 1
Plot_Event.metadict.update(read_archive_line(i))
df = pd.read_csv(filename)
# provided that their lengths match
df.loc[df.index[index], 'Event Check'] = False
df.to_csv(filename)
print(read_archive_line(i))
plot_table = pd.read_csv(Plot_Event.metadict['file_name'], dtype={'STATION_1:SlewRate' : "float64"})
freq_xaxis = np.linspace(0, 18000, 10000)
freq_yaxis = plot_table['STATION_1:Freq']
slew_xaxis = np.linspace(0, 18000, 10000)
slew_yaxis = plot_table['STATION_1:SlewRate']

fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle(Plot_Event.metadict['timestamp'])
ax1.plot(freq_xaxis, freq_yaxis)
ax1.set_title('Frequency')
ax1.set(xlabel='Time in Frames', ylabel='Frequency (Hz)')
ax2.plot(slew_xaxis, slew_yaxis, 'tab:red')
ax2.set(xlabel='Time in Frames', ylabel='Slew Rate')
ax2.set_title('Slew Rate')
canvas = FigureCanvasTkAgg(fig, tab4)  # A tk.DrawingArea.
canvas.draw()

toolbar = CustomToolbar(canvas,tab4)
toolbar.update()
toolbar.pack(side=tk.TOP)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


def on_key_press(event):
    print("you pressed {}".format(event.key))
    if event.key == 'n':
        print("You pressed N!")
        on_key_press(bnext)
    if event.key == 'm':
        print("You pressed M!")
        on_key_press(bprev)
    key_press_handler(event, canvas, toolbar)


canvas.mpl_connect("key_press_event", on_key_press)


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


button = tk.Button(tab4, text="Quit", command=_quit)
button.pack()
bnext = tk.Button(tab4, text="True Event", command = lambda: TrueEvent(i+1))
bnext.pack()
bprev = tk.Button(tab4, text="False Event", command = lambda: FalseEvent(i+1))
bprev.pack()




"""

%%%%% USED FOR SEPARATING METADATA BY SEVERITY %%%%%%

df = pd.read_csv(filename)
dfts = pd.to_datetime(df['timestamp'], errors='coerce')
print(df['severity_desc'][0:5])
major_df = df.loc[df['severity_desc'] =='Major']
major_df =major_df.reset_index()
print(major_df[0:5])
saveas = filedialog.asksaveasfilename(filetypes = (("CSV File", "*.csv"),) ) 
major_df.to_csv(saveas)
minor_df = df.loc[df['severity_desc'] =='Minor']
minor_df =minor_df.reset_index()
print(minor_df[0:5])
minor_df.to_csv(saveas)
none_df = df.loc[df['severity_desc'] =='None']
none_df =none_df.reset_index()
print(none_df[0:5])
none_df.to_csv(saveas)

"""


# Main loop for window. Closes FTP on exit.

root.mainloop()


ftp.quit()