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
file_list = os.listdir(filepath)
for i in file_list:
    fullfile = filepath+'/'+i
    print("Now processing " + fullfile + " .....")
    
    
    def recalculate_slew_rate(window, column_data, start_index):
        print('foo')
        x_list = np.array(range(window))
        x_list = x_list * 0.016
        y_list = np.array(column_data[(start_index-window):start_index])
        x2 = x_list**2
        y2 = y_list**2
        try:
            xy = x_list * y_list 
        except ValueError:
            return
        sumx = np.sum(x_list)
        sumy = np.sum(y_list)
        sumx2 = np.sum(x2)
        sumxy = np.sum(xy)
        slew_rate_point = (window * sumxy - sumx * sumy) / (window*sumx2 - sumx**2)
        return slew_rate_point
    
    
    try:
        try:
            init_table = pd.read_csv(fullfile, encoding='latin_1', 
                                 dtype={'STATION_1:SlewRate': "float64"})
            print("No NaN")
        except TypeError:
            print('Data Type Error, Fixing...')
            init_table = pd.read_csv(fullfile, encoding='iso-8859-1')
            init_table['STATION_1:SlewRate'].replace(regex=True,
                                                     inplace=True,
                                                     to_replace=r'[^0-9.\-E]',
                                                     value=r'')
            init_table['STATION_1:SlewRate'] = init_table['STATION_1:SlewRate'].astype('float64')
            
    except ValueError:
        print("NaN Detected...")
        
        try:
            init_table = pd.read_csv(fullfile, encoding='latin_1', 
                                 dtype={'STATION_1:SlewRate': "float64"})
        except ValueError:
            print('Data Type Error, Fixing...')
            init_table = pd.read_csv(fullfile, encoding='iso-8859-1')
            init_table.replace('#NaN', float(np.nan), inplace=True)
            init_table['STATION_1:SlewRate'].replace(regex=True,
                                                     inplace=True,
                                                     to_replace=r'[^0-9.\-E]',
                                                     value=r'')
            init_table['STATION_1:SlewRate'].replace(regex=True, inplace=True, to_replace=r'[^(\w+\S+)$]', value=np.nan)
            init_table['STATION_1:SlewRate'] = init_table['STATION_1:SlewRate'].astype('float64')
            
        init_table.replace('#NaN', float(np.nan), inplace=True)
        nullmask = init_table.loc[pd.isnull(init_table['STATION_1:Freq'])].index.values.tolist()
        init_table = init_table.drop(nullmask)
        init_table = init_table.reset_index(drop=True)
        
        if nullmask:
                
            if 'STATION_1:SlewRate' in init_table.columns:
                window=350
                freq_data = init_table['STATION_1:Freq'].tolist()
                freq_data = [float(i) for i in freq_data]
                fixed_slews = []
                for i in range(window):
                    fixed_slews.append(recalculate_slew_rate(window, freq_data, nullmask[0]+i))

                try:
                    init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate'] = fixed_slews
                except KeyError:
                    fixed_slews_corrected = [i for i in fixed_slews if i ]
                    init_table.loc[range(nullmask[0]-1, nullmask[0]-1+(len(fixed_slews_corrected))),'STATION_1:SlewRate'] = fixed_slews_corrected

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
                window = 350
                th = 0.0031
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFSlew'] = fixed_flags 
                
            if 'STATION_1:UFSlew' in init_table.columns:
                window = 350
                th = -0.0031
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFSlew'] = fixed_flags
            
            if 'STATION_1:OFT4' in init_table.columns:
                window = 350
                th = 0.004
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT4'] = fixed_flags 
                
            if 'STATION_1:UFT4' in init_table.columns:
                window = 350
                th = -0.004
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT4'] = fixed_flags
            
            if 'STATION_1:OFT5' in init_table.columns:
                window = 350
                th = 0.005
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT5'] = fixed_flags    
                
            if 'STATION_1:UFT5' in init_table.columns:
                window = 350
                th = -0.005
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0) 
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT5'] = fixed_flags
            
            if 'STATION_1:OFT6' in init_table.columns:
                window = 350
                th = 0.006
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT6'] = fixed_flags   
                
            if 'STATION_1:UFT6' in init_table.columns:
                window = 350
                th = -0.006
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0) 
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT6'] = fixed_flags
            
            if 'STATION_1:OFT7' in init_table.columns:
                window = 350
                th = 0.007
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT7'] = fixed_flags     
                
            if 'STATION_1:UFT7' in init_table.columns:
                window = 350
                th = -0.007
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0) 
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT7'] = fixed_flags
            
            if 'STATION_1:OFT8' in init_table.columns:
                window = 350
                th = 0.008
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT8'] = fixed_flags 
                
            if 'STATION_1:UFT8' in init_table.columns:
                window = 350
                th = -0.008
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0) 
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT8'] = fixed_flags
            
            if 'STATION_1:OFT9' in init_table.columns:
                window = 350
                th = 0.009
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT9'] = fixed_flags
                
            if 'STATION_1:UFT9' in init_table.columns:
                window = 350
                th = -0.009
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0) 
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT9'] = fixed_flags
            
            if 'STATION_1:OFT10' in init_table.columns:
                window = 350
                th = 0.01
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT10'] = fixed_flags    
                
            if 'STATION_1:UFT10' in init_table.columns:
                window = 350
                th = -0.01
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:SlewRate']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT10'] = fixed_flags
            
            if 'STATION_1:OFSlew50' in init_table.columns:
                window = 50
                th = 0.0031
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFSlew50'] = fixed_flags 
                
            if 'STATION_1:UFSlew50' in init_table.columns:
                window = 50
                th = -0.0031
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFSlew50'] = fixed_flags    
                
            if 'STATION_1:OFT450' in init_table.columns:
                window = 50
                th = 0.004
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT450'] = fixed_flags  
                
            if 'STATION_1:UFT450' in init_table.columns:
                window = 50
                th = -0.004
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT450'] = fixed_flags  
                
            if 'STATION_1:OFT550' in init_table.columns:
                window = 50
                th = 0.005
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT550'] = fixed_flags  
                
            if 'STATION_1:UFT550' in init_table.columns:
                window = 50
                th = -0.005
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT550'] = fixed_flags      
                
            if 'STATION_1:OFT650' in init_table.columns:
                window = 50
                th = 0.006
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT650'] = fixed_flags      
                
            if 'STATION_1:UFT650' in init_table.columns:
                window = 50
                th = -0.006
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT650'] = fixed_flags  
                
            if 'STATION_1:OFT750' in init_table.columns:
                window = 50
                th = 0.007
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT750'] = fixed_flags      
                
            if 'STATION_1:UFT750' in init_table.columns:
                window = 50
                th = -0.007
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT750'] = fixed_flags      
                
                
            if 'STATION_1:OFT850' in init_table.columns:
                window = 50
                th = 0.008
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT850'] = fixed_flags 
                
            if 'STATION_1:UFT850' in init_table.columns:
                window = 50
                th = -0.008
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT850'] = fixed_flags  
                
            if 'STATION_1:OFT950' in init_table.columns:
                window = 50
                th = 0.009
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT950'] = fixed_flags 
                
            if 'STATION_1:UFT950' in init_table.columns:
                window = 50
                th = -0.009
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT950'] = fixed_flags      
                
            if 'STATION_1:OFT1050' in init_table.columns:
                window = 50
                th = 0.01
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT1050'] = fixed_flags   
                
            if 'STATION_1:UFT1050' in init_table.columns:
                window = 50
                th = -0.01
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew50']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT1050'] = fixed_flags  
                
            if 'STATION_1:OFSlew100' in init_table.columns:
                window = 100
                th = 0.0031
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFSlew100'] = fixed_flags    
                
            if 'STATION_1:UFSlew100' in init_table.columns:
                window = 100
                th = -0.0031
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFSlew100'] = fixed_flags     
                
            if 'STATION_1:OFT4100' in init_table.columns:
                window = 100
                th = 0.004
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT4100'] = fixed_flags        
                
            if 'STATION_1:UFT4100' in init_table.columns:
                window = 100
                th = -0.004
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT4100'] = fixed_flags  
            
            if 'STATION_1:OFT5100' in init_table.columns:
                window = 100
                th = 0.005
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT5100'] = fixed_flags   
                
            if 'STATION_1:UFT5100' in init_table.columns:
                window = 100
                th = -0.005
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT5100'] = fixed_flags      
                
            if 'STATION_1:OFT6100' in init_table.columns:
                window = 100
                th = 0.006
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT6100'] = fixed_flags    
                
            if 'STATION_1:UFT6100' in init_table.columns:
                window = 100
                th = -0.006
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT6100'] = fixed_flags     
                
            if 'STATION_1:OFT7100' in init_table.columns:
                window = 100
                th = 0.007
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT7100'] = fixed_flags    
                
            if 'STATION_1:UFT7100' in init_table.columns:
                window = 100
                th = -0.007
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT7100'] = fixed_flags    
                
            if 'STATION_1:OFT8100' in init_table.columns:
                window = 100
                th = 0.008
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT8100'] = fixed_flags  
                
            if 'STATION_1:UFT8100' in init_table.columns:
                window = 100
                th = -0.008
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT8100'] = fixed_flags  
                
            if 'STATION_1:OFT9100' in init_table.columns:
                window = 100
                th = 0.009
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT9100'] = fixed_flags    
                
            if 'STATION_1:UFT9100' in init_table.columns:
                window = 100
                th = -0.009
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT9100'] = fixed_flags      
                
            if 'STATION_1:OFT10100' in init_table.columns:
                window = 100
                th = 0.01
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT10100'] = fixed_flags    
                
            if 'STATION_1:UFT10100' in init_table.columns:
                window = 100
                th = -0.01
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew100']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT10100'] = fixed_flags   
                
            if 'STATION_1:OFSlew200' in init_table.columns:
                window = 200
                th = 0.0031
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFSlew200'] = fixed_flags 
                
            if 'STATION_1:UFSlew200' in init_table.columns:
                window = 200
                th = -0.0031
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFSlew200'] = fixed_flags    
                
            if 'STATION_1:OFT4200' in init_table.columns:
                window = 200
                th = 0.004
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT4200'] = fixed_flags  
                
            if 'STATION_1:UFT4200' in init_table.columns:
                window = 200
                th = -0.004
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT4200'] = fixed_flags   
                
            if 'STATION_1:OFT5200' in init_table.columns:
                window = 200
                th = 0.005
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT5200'] = fixed_flags   
                
            if 'STATION_1:UFT5200' in init_table.columns:
                window = 200
                th = -0.005
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT5200'] = fixed_flags      
                
            if 'STATION_1:OFT6200' in init_table.columns:
                window = 200
                th = 0.006
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT6200'] = fixed_flags      
                
            if 'STATION_1:UFT6200' in init_table.columns:
                window = 200
                th = -0.006
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT6200'] = fixed_flags   
                
            if 'STATION_1:OFT7200' in init_table.columns:
                window = 200
                th = 0.007
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT7200'] = fixed_flags
                
            if 'STATION_1:UFT7200' in init_table.columns:
                window = 200
                th = -0.007
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT7200'] = fixed_flags    
                
            if 'STATION_1:OFT8200' in init_table.columns:
                window = 200
                th = 0.008
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT8200'] = fixed_flags  
                
            if 'STATION_1:UFT8200' in init_table.columns:
                window = 200
                th = -0.008
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT8200'] = fixed_flags      
                
            if 'STATION_1:OFT9200' in init_table.columns:
                window = 200
                th = 0.009
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT9200'] = fixed_flags  
                
            if 'STATION_1:UFT9200' in init_table.columns:
                window = 200
                th = -0.009
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT9200'] = fixed_flags 
                
            if 'STATION_1:OFT10200' in init_table.columns:
                window = 200
                th = 0.01
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i >= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:OFT10200'] = fixed_flags  
                
            if 'STATION_1:UFT10200' in init_table.columns:
                window = 200
                th = -0.01
                fixed_flags = []
                for i in list(init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:Slew200']):
                    if i <= th:
                        fixed_flags.append(1)
                    else:
                        fixed_flags.append(0)
                init_table.loc[range(nullmask[0], nullmask[0]+window),'STATION_1:UFT10200'] = fixed_flags      
                
        else:
            window = 0
            for i in init_table['STATION_1:SlewRate']:
                if i == np.nan:
                    window = window + 1
                    
            pass
                
        
        init_table.to_csv(fullfile, index=False)
            