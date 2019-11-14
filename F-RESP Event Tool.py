# -*- coding: utf-8 -*-
"""
This is the event processing and plotting program for F-RESP.

READABILITY THINGS IM AWARE OF:
    Names (especially method names) are ambiguous or overly similar
    Some hard coded stuff shouldn't be (options, etc)
    tk stuff uses names I stole from an example, should fix that
    Should rename program for obvious reasons
    Less abbreviations, this isn't a text message
    Press F8
"""

import ftplib
import csv
import os
from ftplib import FTP
import tkinter as tk
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show

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

    def process_event(self, file_path):
        """Preloads an Event's dictionary for future sorting.
            Designed for both initial sorting and archive repair.
            Add new features here. Repair after adding.
        """

        self.metadict['file_name'] = file_path
        print(self.metadict)
        init_table = pd.read_csv(self.metadict['file_name'], encoding='latin_1')

        # init_freq_list = init_table['STATION_1:Freq']

        # init_slew_list = init_table['STATION_1:SlewRate']

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
            # df['DataFrame Column'] = pd.to_numeric(df['DataFrame Column'], errors='coerce')
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


Current_Event = Event() #Program startup initialization.


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
    Current_Event = Event()
    Current_Event.process_event(file_path)
    ftp.delete(i)
    global DL_COUNT
    DL_COUNT = DL_COUNT + 1
    label_counter.configure(text=str(DL_COUNT) +
                            ' files downloaded this session')
    stream_statustxt.update()


def read_archive_line():
    """Opens the archive metadata csv, reads a single line into an event,
    and then closes the archive."""
    pass


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
        for i in archive_file_list:
            file_path = ARCHIVEPATH+i
            Load_Event.process_event(file_path)
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
                Current_Event.write_eventlog()
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


labelvar = "Test FTP Program"

root = tk.Tk()
root.geometry('640x480')
root.title("F-RESP Archived Recording Tool")
frame = tk.Frame(root)
frame.pack()
stream_statustxt = tk.Label(root, text=labelvar)
stream_statustxt.pack()
listbutton = tk.Button(frame,
                       text="Begin FTP stream",
                       command=start_stream)
listbutton.pack()
label_counter = tk.Label(root,
                         text=str(DL_COUNT) + ' files downloaded this session')
label_counter.pack()
PLOTBUTTON = tk.Button(frame,
                       text="Quick Plot",
                       command=Current_Event.quick_plot)
PLOTBUTTON.pack()
archive_remake_button = tk.Button(frame,
                                  text="Remake Archive (!Turn off FTP!!)",
                                  command=update_archive)
archive_remake_button.pack()
# Main loop for window. Closes FTP on exit.
root.mainloop()
ftp.close()
