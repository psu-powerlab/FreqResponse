# -*- coding: utf-8 -*-
"""
This is the event processing and plotting program for F-RESP.

READABILITY THINGS IM AWARE OF:
    Names (especially method names) are ambiguous or overly similar
    Some hard coded stuff shouldn't be (options, etc)
    Should rename program for obvious reasons
    Press F8
    Would be better if GUI process was an object
"""

import ftplib
import csv
import os
from ftplib import FTP
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show
from bokeh.layouts import column
import datetime as dt
from dateutil.parser import parse

ARCHIVEPATH = ('G:/My Drive/PGE Frequency Response/'
               'Archive/')
ftp = FTP('10.208.21.101')
ftp.login('admin', 'TAIL')
ftp.cwd('FILES/Recording')
# This apparently is a keep-alive option for the FTP.
# ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

global DL_COUNT
DL_COUNT = 0


class Event:
    """This is the class that all recordings are sorted into"""
    metadict = {
                'archive_index_number': int(),
                'timestamp': dt.datetime(1970,1,1),
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
            Add new features here. Repair after adding.
        """

        self.metadict['file_name'] = file_path
        print(self.metadict)
        init_table = pd.read_csv(self.metadict['file_name'], encoding='latin_1')

        # init_freq_list = init_table['STATION_1:Freq']

        # init_slew_list = init_table['STATION_1:SlewRate']
        
        init_time_list = init_table['Timestamp']
        init_datetime = parse(init_time_list[0])
        self.metadict['timestamp'] = init_datetime
        print(self.metadict['timestamp'])
        
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

    def quick_plot(self):
        """Generates a plot of the most recent Event instance."""

        try:
            plot_table = pd.read_csv(self.metadict['file_name'])
            x_plot = np.linspace(0, 18000, 18000)
            y_plot = plot_table['STATION_1:Freq']
            plot_qp = figure(title="Current Event",
                             x_axis_label='Time in frames',
                             y_axis_label='Frequency (Hz)')
            plot_qp.line(x_plot, y_plot, legend="Temp.", line_width=2)
            show(plot_qp)
        except FileNotFoundError:
            print('File not found.')

    def write_eventlog(self):
        """Writes the metadict to a line of the metadata file."""
        csv_columns = list(self.metadict.keys())
        csv_file = "test.csv"  # TODO: change
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




def connect_to_ftp():
    """Creates an FTP object with the proper username, password, and path."""

    ftp = FTP('10.208.21.101')
    ftp.login('admin', 'TAIL')
    ftp.cwd('FILES/Recording')


def process_one_file(i):
    """Copies a file from the ftp, runs event processing, and deletes
    the redundant file from the FTP"""

    stream_statustxt.configure(text="Now Processing: " + i)
    file_path = ARCHIVEPATH+i
    localfile = open(file_path, 'wb')
    ftp.retrbinary('RETR '+i, localfile.write, 1024)
    localfile.close()
    new_index = int(Current_Event.metadict['archive_index_number']) + 1
    Current_Event.process_event(file_path, new_index)
    ftp.delete(i)
    global DL_COUNT
    DL_COUNT = DL_COUNT + 1
    label_counter.configure(text=str(DL_COUNT) +
                            ' files downloaded this session')
    stream_statustxt.update()
    Current_Event.write_eventlog()

def repair_junk_data():
    pass

def read_archive_line(line_num):
    """Opens the archive metadata csv, reads a single line, RETURNS THE
    DICTIONARY, and then closes the archive."""
    csv_file = "test.csv"  # TODO: change
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
            file_path = ARCHIVEPATH+i
            Load_Event.process_event(file_path, 0)
            Load_Event.metadict['archive_index_number'] = archive_index_number
            archive_index_number = archive_index_number + 1
            writer.writerow(Load_Event.metadict)


def start_stream():
    """Begins file transfer stream from FTP to the preset download folder.
    Also contains exception handler for FTP kickoff situations.
    If FTP connects, runs process_one_file() for all detected files."""

    listbutton.configure(text="Streaming files...")
    try:
        linelist = ftp.nlst()
        for i in linelist:
            process_one_file(i)
        stream_statustxt.after(60000, start_stream)
    except AttributeError:
        print('Attempting to reconnect to FTP')
        try:
            ftp.close()
            connect_to_ftp()
            linelist = ftp.nlst()
            for i in linelist:
                process_one_file(i)
            stream_statustxt.after(60000, start_stream)
        except:
            print('Reconnection Failed.')
            ftp.close()
            listbutton.configure(text="Begin FTP Stream")
    except ftplib.all_errors:
        print('Attempting to reconnect to FTP')
        try:
            ftp.close()
            connect_to_ftp()
            linelist = ftp.nlst()
            for i in linelist:
                process_one_file(i)
                Current_Event.write_eventlog()
            stream_statustxt.after(60000, start_stream)
        except:
            print('Reconnection Failed.')
            ftp.close()
            listbutton.configure(text="Begin FTP Stream")


def update_archive_tree():
    Tree_Event = Event()
    csv_file = "test.csv"  # TODO: change
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

def tree_plot():
        try:
            Plot_Event=Event()
            Plot_Event.metadict.update(read_archive_line(int(tree.item(tree.focus())['text'])))
            plot_table = pd.read_csv(Plot_Event.metadict['file_name'], dtype={'STATION_1:SlewRate' : "float64"})
            freq_xaxis = np.linspace(0, 18000, 18000)
            freq_yaxis = plot_table['STATION_1:Freq']
            plot_freq = figure(plot_width = 1800, plot_height = 400, title=Plot_Event.metadict['timestamp'],
                             x_axis_label='Time in frames',
                             y_axis_label='Frequency (Hz)',
                             tooltips = [("index", "$index"),
                                         ("Frequency", "$y")])
            plot_freq.line(freq_xaxis, freq_yaxis, legend="Frequency", line_width=1)
            slew_xaxis = np.linspace(0,18000, 18000)
            slew_yaxis = plot_table['STATION_1:SlewRate']
            plot_slew = figure(plot_width = 1800, plot_height = 400, 
                             x_range=plot_freq.x_range,
                             title=Plot_Event.metadict['timestamp'],
                             x_axis_label='Time in frames',
                             y_axis_label='Slew Rate',
                             tooltips = [("index", "$index"),
                                         ("Slew", "$y")])
            plot_slew.line(slew_xaxis, slew_yaxis, legend="Slew Rate", line_width = 1)
            plot_slew.line(slew_xaxis, 0)
            
            show(column(plot_freq, plot_slew))
        except FileNotFoundError:
            print('File not found.')



# course1_assessments.bind("<<TreeviewSelect>>", OnDoubleClick)        
# Initialize first event

Current_Event = Event()
Current_Event.metadict.update(read_archive_line(-1))
print(Current_Event.metadict)


labelvar = "Test FTP Program"

root = tk.Tk()
root.geometry('640x480')
root.title("F-RESP Archived Recording Tool")
tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)

tab_control.add(tab1, text="Main Menu")
tab_control.add(tab2, text="File Tree")
tab_control.add(tab3, text="Options")
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


PLOTBUTTON = tk.Button(tab2,
                       text="Quick Plot",
                       command=Current_Event.quick_plot)
PLOTBUTTON.pack()
tree = ttk.Treeview(tab2)
tree['columns'] = ('datetime', 'of', 'uf', 'ambig', 'severity')
tree.heading('#0', text='#')
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
ploteventbutton = tk.Button(tab2, text="Plot Selected Event", command=tree_plot)
ploteventbutton.pack()
archive_remake_button = tk.Button(tab3,
                                  text="Remake Archive (!Turn off FTP!!)",
                                  command=update_archive)
archive_remake_button.pack()
# Main loop for window. Closes FTP on exit.
root.mainloop()
ftp.close()
