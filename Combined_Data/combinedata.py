# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 17:53:41 2016

@author: admin
"""
import pandas as pd
from dateutil import parser
import datetime as dt

def getTempdata(wdata):
    emptylist=[]
    for time in range(0,len(wdata.index)):    
        emptylist.append(0)
    changedIrr=pd.DataFrame(dict(GH_Changed=emptylist,DNI_Changed=emptylist,DIFF_Changed=emptylist))    
    wdataTemp=pd.concat([wdata,changedIrr], axis=1)    
    return wdataTemp   

x=0

start_yr=2006
end_yr=2007


for year in range (start_yr,end_yr):
    oldfile=pd.read_csv("../data/"+str(year)+".csv")
    oldfile=getTempdata(oldfile)
    newfile=pd.read_csv("../fixed/"+str(year)+".csv")
    outputfile="data/"+str(year)+".csv"
    print len(oldfile)
    
    firstDate=int(float(parser.parse(oldfile.loc[0,'DATE (MM/DD/YYYY)']).strftime('%j')))
    lastDate=int(float(parser.parse(oldfile.loc[len(oldfile)-1,'DATE (MM/DD/YYYY)']).strftime('%j')))
    
    for i in range (firstDate-1,lastDate):
        date = dt.date(year,1,1) + dt.timedelta(int(float(i)))
        date="%d/%d/%d"%(date.month, date.day, date.year)
        if newfile.loc[newfile['DATE (MM/DD/YYYY)']==date].empty:
           newData=oldfile.loc[oldfile['DATE (MM/DD/YYYY)']==date] 
           tempdata=newfile.append(newData)
           newfile=tempdata
    
    newfile.to_csv(outputfile, index=False)

    