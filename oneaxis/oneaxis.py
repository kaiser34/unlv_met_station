# -*- coding: utf-8 -*-

import pandas as pd
from dateutil import parser
import datetime as dt
import os


datafile='meterlog_ronzone.csv'
oneaxis=pd.read_csv(datafile,sep=';')
oneaxis.columns=['GSL_Ronzone','Datetime','KWH']
annualdata=pd.DataFrame()



for year in range (2006,2016):
    for x in range (0,len(oneaxis)):
        datetime=oneaxis.loc[x,'Datetime']
        if str(year) in datetime:
            print datetime
            annualdata=annualdata.append(oneaxis.loc[oneaxis['Datetime']==oneaxis.loc[x,'Datetime']])
    
    annualdata=annualdata[['Datetime','KWH']]
    annualdata.to_csv('data/'+str(year)+'.csv',index=False)
    annualdata=pd.DataFrame()





