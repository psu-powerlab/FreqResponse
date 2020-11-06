import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import datetime as dt
from datetime import timedelta
import time


df1_ori = (pd.read_csv('Aug_25.csv',usecols=['Timestamp'] ,parse_dates=['Timestamp'],engine='python',index_col=None))
df2_ori = (pd.read_csv('Aug_25.csv',usecols=['STATION_1:Freq'] ,engine='python',index_col=None))
df1_Tpmu = (pd.read_csv('2020-10-26-15-54_645.csv',usecols=['Timestamp'],parse_dates=['Timestamp'],engine='python',index_col=None))
df2_fpmu = (pd.read_csv('2020-10-26-15-54_645.csv',usecols=['freq:'] ,engine='python',index_col=None))
df3_Tpmu = (pd.read_csv('2020-10-26-19-26_666.csv',usecols=['Timestamp'],parse_dates=['Timestamp'],engine='python',index_col=None))
df3_fpmu = (pd.read_csv('2020-10-26-19-26_666.csv',usecols=['freq:'] ,engine='python',index_col=None))


def real_time(df1_ori,df2_ori,df1_Tpmu,df2_fpmu,df,df3_Tpmu,df3_fpmu):
	x1 = df2_ori['STATION_1:Freq']
	x2 = df2_fpmu['freq:']
	y1 = [dt.datetime.now() + dt.timedelta(microseconds=i) for i in range(len(x1))]
	y2 = [dt.datetime.now() + dt.timedelta(microseconds=i) for i in range(len(x2))]
	plt.plot(y1,x1,label="Original Data")
	plt.plot(y1,x2,label="PMU Data")
	plt.title('Frequency Event')
	plt.legend()
	plt.grid()
	plt.gcf().autofmt_xdate()
	plt.show()
real_time(df1_ori,df2_ori,df1_Tpmu,df2_fpmu,df,df3_Tpmu,df3_fpmu)
