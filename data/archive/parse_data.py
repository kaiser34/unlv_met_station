# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 15:00:30 2016

@author: admin
"""
import os
import numpy
import pandas as pd



yr_begin=6
yr_end=16

for year in range(yr_begin,yr_end):

    if year == 6 or year == 7:
        dataset=pd.read_csv("2006_2007.csv")
    elif year == 8 or year == 9:
        dataset=pd.read_csv("2008_2009.csv")
    elif year == 10 or year == 11:
        dataset=pd.read_csv("2010_2011.csv")
    elif year == 12 or year == 13:
        dataset=pd.read_csv("2012_2013.csv")
    elif year == 14 or year == 15:
        dataset=pd.read_csv("2014_2015.csv")
    
    if year>=6 and year<=9:
        AMdataset=pd.read_csv("AM2006_2009.csv")
    elif year>=10 and year<=12:
        AMdataseta=pd.read_csv("AM2010_2012.csv")
    elif year>=13 and year<=15:
        AMdataset=pd.read_csv("AM2013_2015.csv")
     
    if year<10:
        date_yr="200"+str(year)
    else:
        date_yr="20"+str(year)
    
    
    data_yr=dataset[dataset['DATE (MM/DD/YYYY)'].str.contains(date_yr)]
    data_yr=data_yr.reset_index(drop=True)
    #data_yr=data_yr.drop('index',1)
    
    AMdata_yr=AMdataset[AMdataset['DATE (MM/DD/YYYY)'].str.contains(date_yr)]
    Airmass=AMdata_yr['Airmass']
    Airmass=Airmass.reset_index()
    Airmass=Airmass.drop('index',1)
    
    newdata=pd.concat([data_yr,Airmass], axis=1)    
    dataset=[]
    data_yr=[]
    AMdata_yr=[]
    
    
    newdata.to_csv("year/"+str(date_yr)+".csv")
    newdata=[]