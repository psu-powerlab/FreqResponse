# -*- coding: utf-8 -*-
"""
Spyder Editor

NaN Repair Tool
7/13/2020 by Sean Keene for Portland State University Power Engineering Group
F-RESP project.

This tool manually corrects an issue with F-RESP Event Files caused by having 
two PMUs connected simultaneously.

7/13 CURRENT STATUS: NaN functionality complete. Remaining work is to write
the threshold recalculation scripts for all possible situations, and the
Overwrite Original File functionality. Current code doesn't work for threshold
(all outputs are zero).
"""

import pandas as pd
import numpy as np
import csv
import os

filepath = 'G:/My Drive/PGE Frequency Response/Nan Script Test/'
filename = '2020-03-18-01-17_1286.csv'
fullfile = filepath + filename



def recalculate_slew_rate(window, column_data, start_index):
    x_list = np.array(range(window))
    x_list = x_list * 0.016
    y_list = np.array(column_data[start_index-window:start_index])
    x2 = x_list**2
    y2 = y_list**2
    xy = x_list * y_list
    sumx = np.sum(x_list)
    sumy = np.sum(y_list)
    sumx2 = np.sum(x2)
    sumxy = np.sum(xy)
    slew_rate_point = (window * sumxy - sumx * sumy) / (window*sumx2 - sumx**2)
    return slew_rate_point
    pass


try:
    init_table = pd.read_csv(fullfile, encoding='latin_1', 
                         dtype={'STATION_1:SlewRate': "float64"})
except ValueError:
    init_table = pd.read_csv(fullfile, encoding = 'latin_1')
    init_table.replace('#NaN', float(np.nan), inplace=True)
    nullmask = init_table.loc[pd.isnull(init_table['STATION_1:Freq'])].index.values.tolist()
    init_table = init_table.drop(nullmask)
    init_table = init_table.reset_index(drop=True)
    if 'STATION_1:SlewRate' in init_table.columns:
        window=350
        freq_data = init_table['STATION_1:Freq'].tolist()
        freq_data = [float(i) for i in freq_data]
        fixed_slews = []
        for i in range(window):
            fixed_slews.append(recalculate_slew_rate(window, freq_data, nullmask[0]+i))
            
        init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate'] = fixed_slews
        pass
    
    if 'STATION_1:Slew50' in init_table.columns:
        window=50
        freq_data = init_table['STATION_1:Freq'].tolist()
        freq_data = [float(i) for i in freq_data]
        fixed_slews = []
        for i in range(window):
            fixed_slews.append(recalculate_slew_rate(window, freq_data, nullmask[0]+i))
            
        init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50'] = fixed_slews
        pass        
    
    if 'STATION_1:Slew100' in init_table.columns:
        window=100
        freq_data = init_table['STATION_1:Freq'].tolist()
        freq_data = [float(i) for i in freq_data]
        fixed_slews = []
        for i in range(window):
            fixed_slews.append(recalculate_slew_rate(window, freq_data, nullmask[0]+i))
            
        init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100'] = fixed_slews
    
    if 'STATION_1:Slew200' in init_table.columns:
        window=200
        freq_data = init_table['STATION_1:Freq'].tolist()
        freq_data = [float(i) for i in freq_data]
        fixed_slews = []
        for i in range(window):
            fixed_slews.append(recalculate_slew_rate(window, freq_data, nullmask[0]+i))
        init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200'] = fixed_slews
    
    if 'STATION_1:OFSlew' in init_table.columns:
        pass
    
    if 'STATION_1:UFSlew' in init_table.columns:
        window = 350
        th = 100
        fixed_flags = []
        for i in range(window):
            fixed_flags.append(1 if i in init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate'] <= th else 0)
        init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFSlew'] = fixed_flags
    
    if 'STATION_1:OFT4' in init_table.columns:
        pass
    
    if 'STATION_1:UFT4' in init_table.columns:
        window = 350
        th = -0.004
        fixed_flags = []
        for i in range(window):
            fixed_flags.append(1 if i in init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate'] <= th else 0)
        init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT4'] = fixed_flags
    
    if 'STATION_1:OFT5' in init_table.columns:
        pass
    
    if 'STATION_1:UFT5' in init_table.columns:
        window = 350
        th = -0.005
        fixed_flags = []
        for i in range(window):
            fixed_flags.append(1 if i in init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate'] <= th else 0)
        init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT5'] = fixed_flags
    
    if 'STATION_1:OFT6' in init_table.columns:
        pass
    
    if 'STATION_1:UFT6' in init_table.columns:
        window = 350
        th = -0.006
        fixed_flags = []
        for i in range(window):
            fixed_flags.append(1 if i in init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate'] <= th else 0)
        init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT6'] = fixed_flags
    
    if 'STATION_1:OFT7' in init_table.columns:
        pass
    
    if 'STATION_1:UFT7' in init_table.columns:
        window = 350
        th = -0.007
        fixed_flags = []
        for i in range(window):
            fixed_flags.append(1 if i in init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate'] <= th else 0)
        init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT7'] = fixed_flags
    
    if 'STATION_1:OFT8' in init_table.columns:
        pass
    
    if 'STATION_1:UFT8' in init_table.columns:
        window = 350
        th = -0.008
        fixed_flags = []
        for i in range(window):
            fixed_flags.append(1 if i in init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate'] <= th else 0)
        init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT8'] = fixed_flags
    
    if 'STATION_1:OFT9' in init_table.columns:
        pass
    
    if 'STATION_1:UFT9' in init_table.columns:
        window = 350
        th = -0.009
        fixed_flags = []
        for i in range(window):
            fixed_flags.append(1 if i in init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate'] <= th else 0)
        init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT9'] = fixed_flags
    
    if 'STATION_1:OFT10' in init_table.columns:
        pass
    
    if 'STATION_1:UFT10' in init_table.columns:
        window = 350
        th = -0.01
        fixed_flags = []
        for i in range(window):
            fixed_flags.append(1 if i in init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate'] <= th else 0)
        init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT10'] = fixed_flags
    
    if 'STATION_1:OFSlew50' in init_table.columns:
        pass
    
    if 'STATION_1:UFSlew50' in init_table.columns:
        pass
    
    if 'STATION_1:OFT450' in init_table.columns:
        pass
    
    if 'STATION_1:UFT450' in init_table.columns:
        pass
    
    if 'STATION_1:OFT550' in init_table.columns:
        pass
    
    if 'STATION_1:UFT550' in init_table.columns:
        pass
    
    if 'STATION_1:OFT650' in init_table.columns:
        pass
    
    if 'STATION_1:UFT650' in init_table.columns:
        pass
    
    if 'STATION_1:OFT750' in init_table.columns:
        pass
    
    if 'STATION_1:UFT750' in init_table.columns:
        pass
    
    if 'STATION_1:OFT850' in init_table.columns:
        pass
    
    if 'STATION_1:UFT850' in init_table.columns:
        pass
    
    if 'STATION_1:OFT950' in init_table.columns:
        pass
    
    if 'STATION_1:UFT950' in init_table.columns:
        pass
    
    if 'STATION_1:OFT1050' in init_table.columns:
        pass
    
    if 'STATION_1:UFT1050' in init_table.columns:
        pass
    
    if 'STATION_1:OFSlew100' in init_table.columns:
        pass
    
    if 'STATION_1:UFSlew100' in init_table.columns:
        pass
    
    if 'STATION_1:OFT4100' in init_table.columns:
        pass
    
    if 'STATION_1:UFT4100' in init_table.columns:
        pass
    
    if 'STATION_1:OFT5100' in init_table.columns:
        pass
    
    if 'STATION_1:UFT5100' in init_table.columns:
        pass
    
    if 'STATION_1:OFT6100' in init_table.columns:
        pass
    
    if 'STATION_1:UFT6100' in init_table.columns:
        pass
    
    if 'STATION_1:OFT7100' in init_table.columns:
        pass
    
    if 'STATION_1:UFT7100' in init_table.columns:
        pass
    
    if 'STATION_1:OFT8100' in init_table.columns:
        pass
    
    if 'STATION_1:UFT8100' in init_table.columns:
        pass
    
    if 'STATION_1:OFT9100' in init_table.columns:
        pass
    
    if 'STATION_1:UFT9100' in init_table.columns:
        pass
    
    if 'STATION_1:OFT10100' in init_table.columns:
        pass
    
    if 'STATION_1:UFT10100' in init_table.columns:
        pass
    
    if 'STATION_1:OFSlew200' in init_table.columns:
        pass
    
    if 'STATION_1:UFSlew200' in init_table.columns:
        pass
    
    if 'STATION_1:OFT4200' in init_table.columns:
        pass
    
    if 'STATION_1:UFT4200' in init_table.columns:
        pass
    
    if 'STATION_1:OFT5200' in init_table.columns:
        pass
    
    if 'STATION_1:UFT5200' in init_table.columns:
        pass
    
    if 'STATION_1:OFT6200' in init_table.columns:
        pass
    
    if 'STATION_1:UFT6200' in init_table.columns:
        pass
    
    if 'STATION_1:OFT7200' in init_table.columns:
        pass
    
    if 'STATION_1:UFT7200' in init_table.columns:
        pass
    
    if 'STATION_1:OFT8200' in init_table.columns:
        pass
    
    if 'STATION_1:UFT8200' in init_table.columns:
        pass
    
    if 'STATION_1:OFT9200' in init_table.columns:
        pass
    
    if 'STATION_1:UFT9200' in init_table.columns:
        pass
    
    if 'STATION_1:OFT10200' in init_table.columns:
        pass
    
    if 'STATION_1:UFT10200' in init_table.columns:
        pass
    
        