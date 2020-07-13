# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
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
    
       