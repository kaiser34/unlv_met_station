# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 13:07:14 2016

@author: Adam Betemedhin
         Center for Energy Research - UNLV
         Met Weather Station - Data Correction Program
         Spring 2016
"""
import pandas as pd
import os
from dateutil import parser
from met_functions import * #Custom python file containing callable functions


mille=2000 #integer representing the century in which the data was collected
DATAFILE_DIR="data/" #Location of the annual data in reference to this source file
param=[]

datafix=pd.read_csv("datafix.csv") #Data File Containing affected days
twork=datafix.loc[datafix['trigger']==1] #DataFrame containing days that triggered an affected status
twork=twork.reset_index(drop=True) #Resets the index [starts from index=0]
work=twork.loc[twork['special']==0] #Dataframe containig days that do not include special circumstances
work=work.reset_index(drop=True)  #Resets the index [starts from index=0]
job_begin=work.loc[0,'date']#First date listed as affected
job_end= work.loc[len(work.index)-1,'date'] #Last date listed as affected
year_begin=parser.parse(job_begin).year #First year listed as affected
year_end=parser.parse(job_end).year #Las year listed as affected  
#Empty unused dataframes
datafix=[] #Empty datafix dataframe
twork=[] #Empty twork dataframe


#Begin data correction
for year in range(year_begin,year_end): #Loop for the number of years
    
    print year
    wdata=getdata(DATAFILE_DIR,year) #Retrieves weather data for the specified year
    jobs_yr=getjobs_yr(year,mille,work) #Retrieves a list affected dates in the specified year
    job_days=len(jobs_yr.index)  #Sums up the number of affected dates for the year
    
    for days in range(102,job_days):  #loop for the number of affected days
        
        job_date=jobs_yr.loc[days,'date'] #Retrieves individual affected dates, based on the value of the parent loops iteration variable
        print job_date        
        param.append(jobs_yr.loc[days,'morning'])#Stores whether the following data requires a morning fix into a paramater array
        param.append(jobs_yr.loc[days,'evening'])#Stores whether the following data requires a evening fix into a paramater array
        param.append(jobs_yr.loc[days,'special'])#Stores whether the following data requires a special fix into a paramater array 
        print str(param[0])+" "+str(param[1])+" "+str(param[2])
        job=wdata.loc[wdata['DATE (MM/DD/YYYY)']==job_date] #Retrieves the data for the job-day from the data for the year
        job=job.reset_index(drop=True)
        job_len=len(job.index)
        modelData=getModel(job_date,param,job)
        modelSData=getSModel(job_date,param,job)
        fixedData=getFixdata(job_date,param,modelData,job)
        print fixedData
        writedata(fixedData,year)
        break
    break
print 'The program has completed!'    
#End data correction
