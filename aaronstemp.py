# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 16:14:49 2016

@author: Aaron Sahm
"""

import numpy
import pandas as pd
import math
import matplotlib.pyplot as plt
from dateutil import parser
from datetime import datetime as dt
from datetime import date
import os
import calendar

#------------------------------------------------------------------------------


def morningDNIfix(date,param,smodel,wdata):
    DNImdif=[]
    DNImdifDER=[]
    DNImdif2DER=[]
    DNIfix=[]
    airmass_time=getAirmass(wdata)
    x=0
    for time in range(airmass_time[0],airmass_time[1]):
        DNImdif.append(smodelDNI[x]-dataDNI[x])
        x=x+1
    
    for time in range(1,len(DNImdif.index)):
        DNImdifDER.append(DNImdif[time]-DNImdif[time-1])
        
    for time in range(1,len(DNImdifDER.index)):
        DNImdif2DER.append(DNImdifDER[time]-DNImdifDER[time-1])
        
    x=0
    for time in range(airmass_time[0],airmass_time[1]):
        if dataZEN[x] <= 80:
            airmass80=x
            break
        x=x+1
        
    for time in range((airmass80-2),0):
        if abs(DNImdif2DER[time]) > 6:
            dipend=time
            multiplier=dataDNI[dipend]/smodelDNI[dipend]
            break
            
    for time in range(0,dipend):
        DNIfix.append(multiplier*smodelDNI[time])
        
    if abs(DNIfix[0]-dataDNI[0]) < 30:
        multiplier2=dataDNI[0]/DNIfix[0]
        for time in range(0,dipend):
            DNIfix[time]=(((1-multiplier2)/(dipend)*(time-dipend)+1)*DNIfix[time])
 
#------------------------------------------------------------------------------
           

def morningGHfix(date,param,model,wdata):
    GHmdif=[]
    GHmdifDER=[]
    GHmdif2DER=[]
    GHfix=[]
    airmass_time=getAirmass(wdata)
    x=0
    for time in range(airmass_time[0],airmass_time[1]):
        GHmdif.append(smodelGH[x]-dataGH[x])
        x=x+1
    
    for time in range(1,len(GHmdif.index)):
        GHmdifDER.append(GHmdif[time]-GHmdif[time-1])
        
    for time in range(1,len(GHmdifDER.index)):
        GHmdif2DER.append(GHmdifDER[time]-GHmdifDER[time-1])
        
    x=0
    for time in range(airmass_time[0],airmass_time[1]):
        if dataZEN(x) <= 80:
            airmass80=x
            break
        x=x+1
        
    for time in range((airmass80-2),0):
        if abs(GHmdif2DER[time]) > 4:
            dipend=time
            multiplier=dataGH[dipend]/smodelGH[dipend]
            break
        
    for time in range(0,dipend):
        GHfix.append(multiplier*smodelGH[time])
        
    if abs(GHfix[0]-dataGH[0]) < 15:
        multiplier2=dataGH[0]/GHfix[0]
        for time in range(0,dipend):
            GHfix[time]=(((1-multiplier2)/(dipend)*(time-dipend)+1)*GHfix[time])

#------------------------------------------------------------------------------            

   
def getsModel(date,param,wdata):
    smodelDNI=smodelGH=smodelDif=[[],[],[]] 
    dataDNI=dataGH=dataDIFF=dataZEN=[[],[],[]] 
    irrtime=[] 
      
    
    date=parser.parse(date)
    year=date.year
    dayofyear=float(date.strftime('%j'))
    date=date.toordinal(date)
    
    if calendar.isleap(year) == True:
        year_days=366
    else:
        year_days=365

    measureDNI_max=wdata.loc[wdata['Direct Normal [W/m^2]'].argmax(),'Direct Normal [W/m^2]']
    if measureDNI_max < 890:
        DNI_max=985
    else:
        DNI_max=measureDNI_max
        
    airmass_time=getAirmass(wdata)
#    print airmass_time
    
    measurGH_max=wdata.loc[wdata['Global Horiz [W/m^2]'].argmax(),'Global Horiz [W/m^2]']
    calcGH_max=(math.pow(math.cos((dayofyear-172)/year_days*math.pi),2)*1060+math.pow(math.sin((dayofyear-172)/year_days*math.pi),2)*560)*(1+abs(0.1152*math.pow(math.cos((dayofyear-80)/year_days*(2*math.pi)),2)))
    
    if (abs(measurGH_max-calcGH_max)>130):
        GH_max=calcGH_max
    else:
        GH_max=measurGH_max
    
    x=0
    if dayofyear >= 355 or dayofyear<= 80:        
        for time in range(airmass_time[0],airmass_time[1]): 
            smodelDNI.append((math.pow(math.cos((dayofyear-80)/year_days*math.pi*2),2)*(1.0622*pow(math.e,-0.092*wdata.loc[time,'Airmass']))+math.pow(math.sin((dayofyear-80)/year_days*math.pi*2),2)*(1.0487*pow(math.e,-0.068*wdata.loc[time,'Airmass'])))*DNI_max)        
            smodelGH.append((math.pow(math.cos((dayofyear-80)/year_days*math.pi*2),2)*1.63605*math.pow(wdata.loc[time,'Airmass'],-1.35768)+math.pow(math.sin((dayofyear-80)/year_days*math.pi*2),2)*2.4927*math.pow(wdata.loc[time,'Airmass'],-1.26142))*GH_max)
            smodelDif.append(smodelGH(x)-smodelDNI(x)*math.cos(wdata.loc[time,'Zenith Angle [degrees]']/180*math.pi))
            x=x+1
    
    elif dayofyear > 80 and dayofyear <= 172:        
        for time in range(airmass_time[0],airmass_time[1]):        
            smodelDNI.append((math.pow(math.cos((dayofyear-80)/year_days*math.pi*2),2)*(1.0622*pow(math.e,-0.092*wdata.loc[time,'Airmass']))+math.pow(math.sin((dayofyear-80)/year_days*math.pi*2),2)*(1.0303*pow(math.e,-0.099*wdata.loc[time,'Airmass'])))*DNI_max)        
            smodelGH.append((math.pow(math.cos((dayofyear-80)/year_days*math.pi*2),2)*1.63605*math.pow(wdata.loc[time,'Airmass'],-1.35768)+math.pow(math.sin((dayofyear-80)/year_days*math.pi*2),2)*1.25632*math.pow(wdata.loc[time,'Airmass'],-1.31889))*GH_max)
            smodelDif.append(smodelGH(x)-smodelDNI(x)*math.cos(wdata.loc[time,'Zenith Angle [degrees]']/180*math.pi))
            x=x+1


    elif dayofyear > 172 and dayofyear <= 264:        
        for time in range(airmass_time[0],airmass_time[1]):
            smodelDNI.append((math.pow(math.cos((dayofyear-172)/year_days*math.pi*2),2)*(1.0303*pow(math.e,-0.099*wdata.loc[time,'Airmass']))+math.pow(math.sin((dayofyear-172)/year_days*math.pi*2),2)*(1.0515*pow(math.e,-0.091*wdata.loc[time,'Airmass'])))*DNI_max)        
            smodelGH.append((math.pow(math.cos((dayofyear-172)/year_days*math.pi*2),2)*1.25632*math.pow(wdata.loc[time,'Airmass'],-1.31889)+math.pow(math.sin((dayofyear-172)/year_days*math.pi*2),2)*1.56904*math.pow(wdata.loc[time,'Airmass'],-1.33958))*GH_max)
            smodelDif.append(smodelGH(x)-smodelDNI(x)*math.cos(wdata.loc[time,'Zenith Angle [degrees]']/180*math.pi))
            x=x+1
           
           
    elif dayofyear > 264 and dayofyear < 355:        
        for time in range(airmass_time[0],airmass_time[1]):
            smodelDNI.append((math.pow(math.cos((dayofyear-264)/year_days*math.pi*2),2)*(1.0515*pow(math.e,-0.091*wdata.loc[time,'Airmass']))+math.pow(math.sin((dayofyear-264)/year_days*math.pi*2),2)*(1.0487*pow(math.e,-0.068*wdata.loc[time,'Airmass'])))*DNI_max)        
            smodelGH.append((math.pow(math.cos((dayofyear-264)/year_days*math.pi*2),2)*1.56904*math.pow(wdata.loc[time,'Airmass'],-1.33958)+math.pow(math.sin((dayofyear-264)/year_days*math.pi*2),2)*2.4927*math.pow(wdata.loc[time,'Airmass'],-1.26142))*GH_max)
            smodelDif.append(smodelGH(x)-smodelDNI(x)*math.cos(wdata.loc[time,'Zenith Angle [degrees]']/180*math.pi))
            x=x+1





def getzenith(wdata,airmassTime):
    start=wdata.PST[wdata.PST=='14:00'].index.tolist()
    zTime=start
    return zTime

#------------------------------------------------------------------------------

def eveningDNIfix(date,param,model,smodel,wdata):
    DNImdif=[]
    DNImdifDER=[]
    DNImdif2DER=[]
    DNIfix=[]
    switch1=0
    switch2=0
    airmass_time=getAirmass(wdata)
    ztime=getzenith(TS)
    x=0
    for time in range(airmass_time[0],airmass_time[1]):
        DNImdif.append(modelDNI[x]-dataDNI[x])
        x=x+1
    
    for time in range(1,len(DNImdif.index)):
        DNImdifDER.append(DNImdif[time]-DNImdif[time-1])
        
    for time in range(1,len(DNImdifDER.index)):
        DNImdif2DER.append(DNImdifDER[time]-DNImdifDER[time-1])
        
    for time in range(ztime[0]-2,ztime[1]-2):
        if abs(DNImdif2DER[time]) > 11:
            dipbegin=time
            if dataZEN[dipbegin]<70:
                multiplier=dataDNI[dipbegin]/modelDNI[dipbegin]
            else:
                multiplier=dataDNI[dipbegin]/smodelDNI[dipbegin]
            break
    
    for time in range(dipbegin,ztime[1]-2):
        if abs(DNImdif2DER[time]) < 7:
            switch1=1
        if switch1==1:
            if abs(DNImdif2DER[time]) > 11:
                switch2=1
        if switch2==1:
            if abs(DNImdif2DER[time]) < 7:
                dipend=time
                if dataZEN[dipbegin]<70:
                    multiplier2=dataDNI[dipend]/modelDNI[dipend]
                else:
                    multiplier2=dataDNI[dipend]/smodelDNI[dipend]
                break

    for time in range(dipbegin,dipend):
        if dataZen[dipbegin]<70:
            DNIfix.append(((multiplier2-multiplier)/(dipend-dipbegin)*(time-dipbegin)+multiplier)*modelDNI[time])
        else:
            DNIfix.append(((multiplier2-multiplier)/(dipend-dipbegin)*(time-dipbegin)+multiplier)*smodelDNI[time])
    
    
    switch1=0
    for time in range((dipend+1),(ztime[1]-2)):
        if abs(DNImdif2DER[time]) < 7:
            switch1=1
            if switch1==1:
                if abs(DNImdif2DER[time]) > 11:
                    dipbegin=time
                    if dataZEN[dipbegin]<70:
                        multiplier=dataDNI[dipbegin]/modelDNI[dipbegin]
                    else:
                        multiplier=dataDNI[dipbegin]/smodelDNI[dipbegin]
                    break
                else:
                    DNIfix.append(dataDNI[time])
        else:
            DNIfix.append(dataDNI[time])
        
        
    for time in range(dipbegin,ztime[1]):
        if dataZen[dipbegin]<70:
            DNIfix.append(multiplier*modelDNI[time])
        else:
            DNIfix.append(multiplier*smodelDNI[time])
    
    if abs(DNIfix[ztime[1]]-dataDNI[ztime[1]]) < 30:
        multiplier2=dataDNI[ztime[1]]/DNIfix[ztime[1]]
        for time in range(dipbegin,ztime[1]):
            DNIfix[time]=(((multiplier2-1)/(ztime[1]-dipbegin)*(time-dipbegin)+1)*DNIfix[time])
            


#------------------------------------------------------------------------------

def eveningGHfix(date,param,model,smodel,wdata):
    GHmdif=[]
    GHmdifDER=[]
    GHmdif2DER=[]
    DNImdif=[]
    DNImdifDER=[]
    DNImdif2DER=[]
    GHfix=[]
    switch1=0
    switch2=0
    airmass_time=getAirmass(wdata)
    ztime=getzenith(TS)
    x=0
    for time in range(airmass_time[0],airmass_time[1]):
        GHmdif.append(modelGH[x]-dataGH[x])
        DNImdif.append(modelDNI[x]-dataDNI[x])
        x=x+1
    
    for time in range(1,len(GHmdif.index)):
        GHmdifDER.append(GHmdif[time]-GHmdif[time-1])
        DNImdifDER.append(DNImdif[time]-DNImdif[time-1])
        
    for time in range(1,len(GHmdifDER.index)):
        GHmdif2DER.append(GHmdifDER[time]-GHmdifDER[time-1])
        DNImdif2DER.append(DNImdifDER[time]-DNImdifDER[time-1])
        
    for time in range(ztime[0]-2,ztime[1]-2):
        if abs(GHmdif2DER[time]) > 10:
            dipbegin=time
            if dataZEN[dipbegin]<70:
                multiplier=dataGH[dipbegin]/modelGH[dipbegin]
            else:
                multiplier=dataGH[dipbegin]/smodelGH[dipbegin]
            break
    
    for time in range(dipbegin,ztime[1]-2):
        if abs(GHmdif2DER[time]) < 10:
            switch1=1
        if switch1==1:
            if abs(GHmdif2DER[time]) > 10:
                switch2=1
        if switch2==1:
            if abs(GHmdif2DER[time]) < 10:
                dipend=time
                if dataZEN[dipbegin]<70:
                    multiplier2=dataGH[dipend]/modelGH[dipend]
                else:
                    multiplier2=dataGH[dipend]/smodelGH[dipend]
                break

    for time in range(dipbegin,dipend):
        if dataZen[dipbegin]<70:
            GHfix.append(((multiplier2-multiplier)/(dipend-dipbegin)*(time-dipbegin)+multiplier)*modelGH[time])
        else:
            GHfix.append(((multiplier2-multiplier)/(dipend-dipbegin)*(time-dipbegin)+multiplier)*smodelGH[time])
    
    
    switch1=0
    for time in range((dipend+1),(ztime[1]-2)):
        if abs(GHmdif2DER[time]) < 10:
            switch1=1
            if switch1==1:
                if abs(GHmdif2DER[time]) > 10:
                    dipbegin=time
                    if dataZEN[dipbegin]<70:
                        multiplier=dataGH[dipbegin]/modelGH[dipbegin]
                    else:
                        multiplier=dataGH[dipbegin]/smodelGH[dipbegin]
                    break
                else:
                    GHfix.append(dataGH[time])
        else:
            GHfix.append(dataGH[time])
        
        
    for time in range(dipbegin,ztime[1]):
        if dataZen[dipbegin]<70:
            GHfix.append(multiplier*modelGH[time])
        else:
            GHfix.append(multiplier*smodelGH[time])
    
    if abs(GHfix[ztime[1]]-dataGH[ztime[1]]) < 15:
        multiplier2=dataGH[ztime[1]]/GHfix[ztime[1]]
        for time in range(dipbegin,ztime[1]):
            GHfix[time]=(((multiplier2-1)/(ztime[1]-dipbegin)*(time-dipbegin)+1)*GHfix[time])