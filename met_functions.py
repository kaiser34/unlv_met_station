# -*- coding: utf-8 -*-

#import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from dateutil import parser
#from datetime import datetime as dt
from datetime import date
import os
import calendar

#------------------------------------------------------------------------------
def flagerror(message):
    print message
    exit
    
#------------------------------------------------------------------------------
def getslope(x1,y1,x2,y2):
    x2 = float(x2 - x1)
    y2 = float(y2 - y1)
    m = (y2/x2)
    return m
    
#------------------------------------------------------------------------------    
def getdata(filedir,year):
    file_yr=filedir+str(year)+'.csv'
    try:
        wdata=pd.read_csv(file_yr)
    except:
        print "No more files man!"
        flagerror('Dir or Filename '+str(file_yr)+' does not exist')
        wdata.drop("Unnamed: 0", axis=1, inplace=True)    
    wdata.drop("Unnamed: 0", axis=1, inplace=True)
    return wdata

#------------------------------------------------------------------------------
def getjobs_yr(year, mille,work):
    date_yr=str(year-mille)
    if float(date_yr)<10:
        date_yr=date_yr.zfill(2)
    job_yr=work[work['date'].str.contains(date_yr)]
    job_yr=job_yr.reset_index(drop=True)
    return job_yr
    
#------------------------------------------------------------------------------
def graphdata(fixedData,wdata,case):
    airmass=getAirmass(wdata)
    dataGH=dataDNI=PST=[[],[],[]] 
    
    for i in range (airmass[0],airmass[1]):
        dataDNI.append(wdata.loc[i,'Direct Normal [W/m^2]'])
        dataGH.append(wdata.loc[i,'Global Horiz [W/m^2]'])
        PST.append(wdata.loc[i,'PST'])
    if len(fixedData)==2:
        tempdata=pd.DataFrame(dict(Time=PST,DataDNI=dataDNI, DataGH=dataGH, FixedDNI=fixedData[0], FixedGH=fixedData[1]))
    elif case == 'GH':
        tempdata=pd.DataFrame(dict(Time=PST,DataDNI=dataDNI, DataGH=dataGH,FixedGH=fixedData))
    elif case =='DNI':
        tempdata=pd.DataFrame(dict(Time=PST,DataDNI=dataDNI, DataGH=dataGH, FixedDNI=fixedData))

    tempdata.reset_index(drop=True)
    tempdata=tempdata.set_index('Time')
    tempdata.plot()
    pass

#------------------------------------------------------------------------------
def prompt(message):
    return str(raw_input(message+'')).lower().strip()

#------------------------------------------------------------------------------
def buildWdata(fixedDNI,fixedGH,wdata):
    airmass=getAirmass(wdata)    
    x=0    
    if len(fixedDNI) != 0:
        for i in range (airmass[0],airmass[1]):        
            if wdata.loc[i,'Direct Normal [W/m^2]'] != fixedDNI[x]:
                wdata.loc[i,'Direct Normal [W/m^2]'] = fixedDNI[x]
                wdata.loc[i,'DNI_Changed']=1
                wdata.loc[i,'DIFF_Changed']=1
            x=x+1
            
    x=0
    if len(fixedGH) != 0:
        for i in range (airmass[0],airmass[1]):        
            if wdata.loc[i,'Global Horiz [W/m^2]'] != fixedGH[x]:
                 wdata.loc[i,'Global Horiz [W/m^2]'] = fixedGH[x]
                 wdata.loc[i,'GH_Changed']=1
                 wdata.loc[i,'DIFF_Changed']=1
            x=x+1
    
    
    
    return wdata
    
#------------------------------------------------------------------------------
    
def calcdiff(wdata):
    airmass_time=getAirmass(wdata)
    for time in range (airmass_time[0],airmass_time[1]):
        if (wdata.loc[time,'DIFF_Changed'])==1:
            wdata.loc[time,'Diffuse Horiz (calc) [W/m^2]']=(wdata.loc[time,'Global Horiz [W/m^2]']-wdata.loc[time,'Direct Normal [W/m^2]']*math.cos((wdata.loc[time,'Zenith Angle [degrees]']/180)*math.pi))
#------------------------------------------------------------------------------
            
position=[] #global variable position
fig=0 #global variable position
cid=0 #global variable position
def manualDatafix(fixedData,wdata,case):
    dataDNI=dataGH=PST=[]    
    airmass=getAirmass(wdata)    
    for i in range (airmass[0],airmass[1]):
        dataDNI.append(wdata.loc[i,'Direct Normal [W/m^2]'])
        dataGH.append(wdata.loc[i,'Global Horiz [W/m^2]'])
        PST.append(wdata.loc[i,'PST'])
   
    tempdata=pd.DataFrame(dict(Time=PST,DataDNI=dataDNI, DataGH=dataGH))
    fig = plt.figure()
    tempdata = fig.add_subplot(111)
    tempdata.plot()

def onclick(event):
    if fig.canvas.manager.toolbar._active is None:
        print 'xdata=%f, ydata=%f'%(event.xdata, event.ydata)
        position.append([event.xdata,event.ydata])
cid = fig.canvas.mpl_connect('button_press_event', onclick)
    
    
    

#------------------------------------------------------------------------------

def getTempdata(wdata):
    emptylist=[]
    for time in range(0,len(wdata.index)):    
        emptylist.append(0)
    changedIrr=pd.DataFrame(dict(GH_Changed=emptylist,DNI_Changed=emptylist,DIFF_Changed=emptylist))    
    wdataTemp=pd.concat([wdata,changedIrr], axis=1)    
    return wdataTemp   

#------------------------------------------------------------------------------
def writedata(data,year):    
    if type(data) != int: #checks to see if get_irrstatus returned an int holding a 0 value instead of a dataframe
            if not data.empty:            
                filename='fixed/'+str(year)+'.csv'
#                print filename
                if os.path.isfile(filename):
                   print 'Appending existing dataframe: '+filename
                   #Grab data from file
                   newdata=pd.read_csv(filename)
                   newdata=pd.concat([newdata,data], axis=1)
                   newdata.to_csv(filename, index=False)
                else:
                   print'Creating new dataframe: '+filename
                   data.to_csv(filename, index=False)
                   #Create new data file from fixed data
    return 0
#------------------------------------------------------------------------------
def getAirmass(wdata):
    airmassTime=[]
    for index in range (0,1439):
        zenith=wdata.loc[index,'Zenith Angle [degrees]']
        if zenith <= 85:
            airmassTime.append(index)
            for index2 in range (index+1,1439 ):
                zenith=wdata.loc[index2,'Zenith Angle [degrees]']
                if zenith >=85:
                    airmassTime.append(index2)
                    break
                
            break
    return airmassTime   

#------------------------------------------------------------------------------  
def getdnistart(datefix,airmass_Time):
    datefix=parser.parse(datefix)
    dayofyear=float(date.strftime('%j'))
    
    start=NIPSHADE.PST[NIPSHADE.PST=='14:00'].index.tolist()
    for time in range(start,airmass_Time[1]):
        if nipshade[time]==1:
            nstart=[time-5,airmass_Time[1]]
            return nstart
        if time==airmass_Time[1]:
            print 'No shading from Amonix found'
            return 0


def getghstart(datefix,airmass_Time):
    datefix=parser.parse(datefix)
    dayofyear=float(date.strftime('%j'))
    
    start=GHSHADE.PST[GHSHADE.PST=='14:00'].index.tolist()
    for time in range(start,airmass_Time[1]):
        if ghshade[time]==1:
            nstart=[time-5,airmass_Time[1]]
            return nstart
        if time==airmass_Time[1]:
            print 'No shading from Amonix or weather pole found'
            return 0

#------------------------------------------------------------------------------  
      
def getModel(datefix,param,wdata):
    modelDNI=modelGH=modelDif=[[],[],[]] 
    dataDNI=dataGH=dataDIFF=dataZEN=[[],[],[]] 
    irrtime=[] 
      
    
    datefix=parser.parse(datefix)
    year=datefix.year
    dayofyear=float(date.strftime('%j'))
    datefix=datefix.toordinal(datefix)
    
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
    x=0
    if dayofyear >= 355 or dayofyear<= 80:        
        for time in range(airmass_time[0],airmass_time[1]): 
            modelDNI.append((math.pow(math.cos((dayofyear-80)/year_days*math.pi*2),2)*(-0.00047388*pow(wdata.loc[time,'Airmass'],3)+0.0126193*pow(wdata.loc[time,'Airmass'],2)-0.15237986*wdata.loc[time,'Airmass']+1.1666472)+math.pow(math.sin((dayofyear-80)/year_days*math.pi*2),2)*(-0.00033031*pow(wdata.loc[time,'Airmass'],3)+0.01115963*pow(wdata.loc[time,'Airmass'],2)-0.15967752*wdata.loc[time,'Airmass']+1.26584657))*DNI_max)        
            modelDif.append((math.pow(math.cos((dayofyear-80)/year_days*math.pi*2),2)*(0.000667*pow(modelDNI[x],1.688571))+math.pow(math.sin((dayofyear-80)/year_days*math.pi*2),2)*(0.000212*pow(modelDNI[x],1.840543))))
            modelGH.append(modelDNI[x]*math.cos((wdata.loc[time,'Zenith Angle [degrees]']/180)*math.pi)+modelDif[x])         
            x=x+1
    
    elif dayofyear > 80 and dayofyear <= 172:        
        for time in range(airmass_time[0],airmass_time[1]):        
            modelDNI.append((math.pow(math.cos((dayofyear-80)/year_days*math.pi*2),2)*(-0.00047388*pow(wdata.loc[time,'Airmass'],3)+0.0126193*pow(wdata.loc[time,'Airmass'],2)-0.15237986*wdata.loc[time,'Airmass']+1.1666472)+math.pow(math.sin((dayofyear-80)/year_days*math.pi*2),2)*(-0.00093561*pow(wdata.loc[time,'Airmass'],3)+0.01862888*pow(wdata.loc[time,'Airmass'],2)-0.17252031*wdata.loc[time,'Airmass']+1.14785839))*DNI_max)        
            modelDif.append((math.pow(math.cos((dayofyear-80)/year_days*math.pi*2),2)*(0.000667*pow(modelDNI[x],1.688571))+math.pow(math.sin((dayofyear-80)/year_days*math.pi*2),2)*(0.00019*pow(modelDNI[x],1.908004))))
            modelGH.append(modelDNI[x]*math.cos((wdata.loc[time,'Zenith Angle [degrees]']/180)*math.pi)+modelDif[x])         
            x=x+1


    elif dayofyear > 172 and dayofyear <= 264:        
        for time in range(airmass_time[0],airmass_time[1]):
           modelDNI.append((math.pow(math.cos((dayofyear-172)/year_days*math.pi*2),2)*(-0.00093561*pow(wdata.loc[time,'Airmass'],3)+0.01862888*pow(wdata.loc[time,'Airmass'],2)-0.17252031*wdata.loc[time,'Airmass']+1.14785839)+math.pow(math.sin((dayofyear-172)/year_days*math.pi*2),2)*(-0.00063359*pow(wdata.loc[time,'Airmass'],3)+0.0147007*pow(wdata.loc[time,'Airmass'],2)-0.15945541*wdata.loc[time,'Airmass']+1.17200587))*DNI_max)        
           modelDif.append((math.pow(math.cos((dayofyear-172)/year_days*math.pi*2),2)*(0.00019*pow(modelDNI[x],1.908004))+math.pow(math.sin((dayofyear-172)/year_days*math.pi*2),2)*(0.000041*pow(modelDNI[x],2.106398))))
           modelGH.append(modelDNI[x]*math.cos((wdata.loc[time,'Zenith Angle [degrees]']/180)*math.pi)+modelDif[x])         
           x=x+1
           
           
    elif dayofyear > 264 and dayofyear < 355:        
        for time in range(airmass_time[0],airmass_time[1]):
           modelDNI.append((math.pow(math.cos((dayofyear-264)/year_days*math.pi*2),2)*(-0.00063359*pow(wdata.loc[time,'Airmass'],3)+0.01470007*pow(wdata.loc[time,'Airmass'],2)-0.15945541*wdata.loc[time,'Airmass']+1.7200587)+math.pow(math.sin((dayofyear-264)/year_days*math.pi*2),2)*(-0.00050005*pow(wdata.loc[time,'Airmass'],3)+0.01188507*pow(wdata.loc[time,'Airmass'],2)-0.1409544*wdata.loc[time,'Airmass']+1.22407448))*DNI_max)        
           modelDif.append((math.pow(math.cos((dayofyear-264)/year_days*math.pi*2),2)*(0.000041*pow(modelDNI[x],2.106398))+math.pow(math.sin((dayofyear-264)/year_days*math.pi*2),2)*(0.000212*pow(modelDNI[x],1.840543))))    
           modelGH.append(modelDNI[x]*math.cos((wdata.loc[time,'Zenith Angle [degrees]']/180)*math.pi)+modelDif[x])         
           x=x+1

    
    for time in range (airmass_time[0],airmass_time[1]):
        irrtime.append(wdata.loc[time,'PST'])
    
    for time in range (airmass_time[0],airmass_time[1]):
        dataDNI.append(wdata.loc[time,'Direct Normal [W/m^2]'])
    
    for time in range (airmass_time[0],airmass_time[1]):
        dataGH.append(wdata.loc[time,'Global Horiz [W/m^2]'])
        
    for time in range (airmass_time[0],airmass_time[1]):#used later in solving for fixed diffused 
        dataDIFF.append(wdata.loc[time,'Diffuse Horiz (calc) [W/m^2]'])
        
    for time in range (airmass_time[0],airmass_time[1]):#used later in solving for fixed diffused 
        dataZEN.append(wdata.loc[time,'Zenith Angle [degrees]'])
        
        
    tempdata=pd.DataFrame(dict(PST=irrtime,ModelDNI=modelDNI,DataDNI=dataDNI,ModelGH=modelGH,DataGH=dataGH,ModelDif=modelDif,DataDIFF=dataDIFF,DataZEN=dataZEN))
    tempdata.reset_index(drop=True)
    tempdata=tempdata.set_index('PST')
#    plt.gca().set_color_cycle(['black', 'red','blue'])
#    tempdata.plot()
    return tempdata
#------------------------------------------------------------------------------

def getSModel(date,param,wdata):
    smodelDNI=smodelGH=smodelDif=[[],[],[]] 
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


    for time in range (airmass_time[0],airmass_time[1]):
        irrtime.append(wdata.loc[time,'PST'])
        
    tempdata=pd.DataFrame(dict(PST=irrtime,SModelDNI=smodelDNI,SModelGH=smodelGH,SModelDif=smodelDif))
    tempdata.reset_index(drop=True)
    tempdata=tempdata.set_index('PST')
    return tempdata
#   plt.gca().set_color_cycle(['black', 'red','blue'])
#    tempdata.plot()


#------------------------------------------------------------------------------


def morningDNIfix(date,param,wdata):
    DNImdif=[]
    DNImdifDER=[]
    DNImdif2DER=[]
    DNIfix=[]
    airmass_time=getAirmass(wdata)
    smodel=getModel(date,param,wdata)
    model=getModel(date,param,wdata)

    x=0
    for time in range(airmass_time[0],airmass_time[1]):
        DNImdif.append(smodel.loc(x,'SModelDNI')-model.loc(x,'DataDNI'))
        x=x+1
    
    for time in range(1,len(DNImdif.index)):
        DNImdifDER.append(DNImdif[time]-DNImdif[time-1])
        
    for time in range(1,len(DNImdifDER.index)):
        DNImdif2DER.append(DNImdifDER[time]-DNImdifDER[time-1])
        
    x=0
    for time in range(airmass_time[0],airmass_time[1]):
        if model.loc(x,'DataZEN') <= 80:
            airmass80=x
            break
        x=x+1
        
    for time in range((airmass80-2),0):
        if abs(DNImdif2DER[time]) > 6:
            dipend=time
            multiplier=model.loc(time,'DataDNI')/smodel.loc(time,'SModelDNI')
            break
            
    for time in range(0,dipend):
        DNIfix.append(multiplier*smodel.loc(time,'SModelDNI'))
        
    if abs(DNIfix[0]-model.loc(0,'DataDNI')) < 30:
        multiplier2=model.loc(0,'DataDNI')/DNIfix[0]
        for time in range(0,dipend):
            DNIfix[time]=(((1-multiplier2)/(dipend)*(time-dipend)+1)*DNIfix[time])
    
    return DNIfix
    
#------------------------------------------------------------------------------
           

def morningGHfix(date,param,wdata):
    GHmdif=[]
    GHmdifDER=[]
    GHmdif2DER=[]
    GHfix=[]
    smodel=getSModel(date,param, wdata)
    model=getModel(date,param,wdata)
    airmass_time=getAirmass(wdata)
    x=0
    for time in range(airmass_time[0],airmass_time[1]):
        GHmdif.append(smodel.loc(x,'SModelGH')-model.loc(x,'DataGH'))
        x=x+1
    
    for time in range(1,len(GHmdif.index)):
        GHmdifDER.append(GHmdif[time]-GHmdif[time-1])
        
    for time in range(1,len(GHmdifDER.index)):
        GHmdif2DER.append(GHmdifDER[time]-GHmdifDER[time-1])
        
    x=0
    for time in range(airmass_time[0],airmass_time[1]):
        if model.loc(x,'DataZEN') <= 80:
            airmass80=x
            break
        x=x+1
        
    for time in range((airmass80-2),0):
        if abs(GHmdif2DER[time]) > 4:
            dipend=time
            multiplier=model.loc(time,'DataGH')/smodel.loc(time,'SModelGH')
            break
        
    for time in range(0,dipend):
        GHfix.append(multiplier*smodel.loc(time,'SModelGH'))
        
    if abs(GHfix[0]-model.loc(0,'DataGH')) < 15:
        multiplier2=model.loc(0,'DataGH')/GHfix[0]
        for time in range(0,dipend):
            GHfix[time]=(((1-multiplier2)/(dipend)*(time-dipend)+1)*GHfix[time])

    return GHfix
    
#------------------------------------------------------------------------------            

def eveningDNIfix(date,param,wdata):
    DNImdif=[]
    DNImdifDER=[]
    DNImdif2DER=[]
    DNIfix=[]
    switch1=0
    switch2=0
    airmass_time=getAirmass(wdata)
    smodel=getSModel(date,param, wdata)
    model=getModel(date,param,wdata)
    ztime=getdnistart(date,airmass_time)
    
    x=0
    for time in range(airmass_time[0],airmass_time[1]):
        DNImdif.append(model.loc(x,'ModelDNI')-model.loc(x,'DataDNI'))
        x=x+1
    
    for time in range(1,len(DNImdif.index)):
        DNImdifDER.append(DNImdif[time]-DNImdif[time-1])
        
    for time in range(1,len(DNImdifDER.index)):
        DNImdif2DER.append(DNImdifDER[time]-DNImdifDER[time-1])
        
    for time in range(ztime[0]-2,ztime[1]-2):
        if abs(DNImdif2DER[time]) > 11:
            dipbegin=time
            if model.loc(dipbegin,'DataZEN')<70:
                multiplier=model.loc(dipbegin,'DataDNI')/model.loc(dipbegin,'ModelDNI')
            else:
                multiplier=model.loc(dipbegin,'DataDNI')/smodel.loc(dipbegin,'SModelDNI')
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
                if model.loc(dipbegin,'DataZEN')<70:
                    multiplier2=model.loc(dipend,'DataDNI')/model.loc(dipend,'ModelDNI')
                else:
                    multiplier2=model.loc(dipend,'DataDNI')/smodel.loc(dipend,'SModelDNI')
                break

    for time in range(dipbegin,dipend):
        if model.loc(dipbegin,'DataZEN')<70:
            DNIfix.append(((multiplier2-multiplier)/(dipend-dipbegin)*(time-dipbegin)+multiplier)*model.loc(time,'ModelDNI'))
        else:
            DNIfix.append(((multiplier2-multiplier)/(dipend-dipbegin)*(time-dipbegin)+multiplier)*smodel.loc(time,'SModelDNI'))
    
    
    switch1=0
    for time in range((dipend+1),(ztime[1]-2)):
        if abs(DNImdif2DER[time]) < 7:
            switch1=1
            if switch1==1:
                if abs(DNImdif2DER[time]) > 11:
                    dipbegin=time
                    if model.loc(dipbegin,'DataZEN')<70:
                        multiplier=model.loc(dipbegin,'DataDNI')/model.loc(dipbegin,'ModelDNI')
                    else:
                        multiplier=model.loc(dipbegin,'DataDNI')/smodel.loc(dipbegin,'SModelDNI')
                    break
                else:
                    DNIfix.append(model.loc(time,'DataDNI'))
        else:
            DNIfix.append(model.loc(time,'DataDNI'))
        
        
    for time in range(dipbegin,ztime[1]):
        if model.loc(dipbegin,'DateZEN')<70:
            DNIfix.append(multiplier*model.loc(time,'ModelDNI'))
        else:
            DNIfix.append(multiplier*smodel.loc(time,'SModelDNI'))
    
    if abs(DNIfix[ztime[1]]-model.loc(ztime[1],'DataDNI')) < 30:
        multiplier2=model.loc(ztime[1],'DataDNI')/DNIfix[ztime[1]]
        for time in range(dipbegin,ztime[1]):
            DNIfix[time]=(((multiplier2-1)/(ztime[1]-dipbegin)*(time-dipbegin)+1)*DNIfix[time])
    
    return DNIfix
#------------------------------------------------------------------------------
def eveningGHfix(date,param,wdata):
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
    smodel=getSModel(date,param, wdata)
    model=getModel(date,param,wdata)
    ztime=getghstart(date,airmass_time)
    
    
    x=0
    for time in range(airmass_time[0],airmass_time[1]):
        GHmdif.append(model.loc(x,'ModelGH')-model.loc(x,'DataGH'))
        DNImdif.append(model.loc(x,'ModelDNI')-model.loc(x,'DataDNI'))
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
            if model.loc(dipbegin,'DataZEN')<70:
                multiplier=model.loc(dipbegin,'DataGH')/model.loc(dipbegin,'ModelGH')
            else:
                multiplier=model.loc(dipbegin,'DataGH')/smodel.loc(dipbegin,'SModelGH')
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
                if model.loc(dipbegin,'DataZEN')<70:
                    multiplier2=model.loc(dipend,'DataGH')/model.loc(dipend,'ModelGH')
                else:
                    multiplier2=model.loc(dipend,'DataGH')/smodel.loc(dipend,'SModelGH')
                break

    for time in range(dipbegin,dipend):
        if model.loc(dipbegin,'DataZEN')<70:
            GHfix.append(((multiplier2-multiplier)/(dipend-dipbegin)*(time-dipbegin)+multiplier)*model.loc(time,'ModelGH'))
        else:
            GHfix.append(((multiplier2-multiplier)/(dipend-dipbegin)*(time-dipbegin)+multiplier)*smodel.loc(time,'SModelGH'))
    
    
    switch1=0
    for time in range((dipend+1),(ztime[1]-2)):
        if abs(GHmdif2DER[time]) < 10:
            switch1=1
            if switch1==1:
                if abs(GHmdif2DER[time]) > 10:
                    dipbegin=time
                    if  model.loc(dipbegin,'DataZEN')<70:
                        multiplier=model.loc(dipbegin,'DataGH')/model.loc(dipbegin,'ModelGH')
                    else:
                        multiplier=model.loc(dipbegin,'DataGH')/smodel.loc(dipbegin,'SModelGH')
                    break
                else:
                    GHfix.append(model.loc(time,'DataGH'))
        else:
            GHfix.append(model.loc(time,'DataGH'))
        
        
    for time in range(dipbegin,ztime[1]):
        if model.loc(dipbegin,'DataZEN')<70:
            GHfix.append(multiplier*model.loc(time,'ModelGH'))
        else:
            GHfix.append(multiplier*smodel.loc(time,'SModelGH'))
    
    if abs(GHfix[ztime[1]]-model.loc(ztime[1],'DataGH')) < 15:
        multiplier2=model.loc(ztime[1],'DataGH')/GHfix[ztime[1]]
        for time in range(dipbegin,ztime[1]):
            GHfix[time]=(((multiplier2-1)/(ztime[1]-dipbegin)*(time-dipbegin)+1)*GHfix[time])
    
    return GHfix
#------------------------------------------------------------------------------








































































#------------------------------------------------------------------------------
def getFixdata(datefix,param,model,wdata):
    fixedData=[]
    fixedGH=[]
    fixedDNI=[]
    response=0
    
    if param[2]==1:
        case='special'
        while(response == 1):
            sensor=prompt('Which Irradiance sensor is being worked on manually? 1=none, 2=GH, 3=DNI, & 4=both')
            if sensor == 1:                
                return 0
            if sensor == 2:
                fixedGH=manualDatafix(wdata,'GH')
                graphdata(fixedGH,wdata,'GH')
            if sensor == 3:
                fixedDNI=manualDatafix(wdata,'DNI')
                graphdata(fixedDNI,wdata,'DNI')
            if sensor == 4:
                fixedGH=manualDatafix(wdata,'GH')
                fixedDNI=manualDatafix(wdata,'DNI')
                graphdata(fixedData[fixedGH,fixedDNI],wdata,case)
            response=prompt('Are the Changes Acceptable? 1=yes , 0=no')
    else:
        if param[0] == 0 and param[1] == 0:
            return 0
    
        if param[0] == 0 and param[1] == 1:
            fixedData.append(eveningDNIfix(datefix,param,model,wdata))
            fixedData.append(eveningGHfix(datefix,param,model,wdata))
            case='evening'
            
        if param[0] == 1 and param[1] == 0:
            fixedData.append(morningDNIfix(datefix,param,model,wdata))
            fixedData.append(morningGHfix(datefix,param,model,wdata))
            case='morning'         
    
        if param[0] == 1 and param[1] == 1:
            fixedData.append(morningDNIfix(datefix,param,model,wdata))
            fixedData.append(morningGHfix(datefix,param,model,wdata))
            fixedData.append(eveningDNIfix(datefix,param,model,wdata))
            fixedData.append(eveningGHfix(datefix,param,model,wdata))
            case='both'
    
     
        graphdata(fixedData,wdata,case)
        response=prompt('Are the Changes Acceptable? 1=yes for both, 2=only DNI, 3=only GH, 4=manual fix')
        
        if response == 1:
            if case == 'evening':
                fixedDNI=fixedData[0]
                fixedGH=fixedData[1]

            if case == 'morning':
                fixedDNI=fixedData[0]
                fixedGH=fixedData[1]
            
            if case == 'both':
                fixedDNI=fixedData[0,2]
                fixedGH=fixedData[1,3]
            
            
        if response == 2:
            if case == 'evening':
                fixedDNI=fixedData[0]
                response=prompt('Does GH need fixing? 1=yes, 0=no')
                while(response == 1):
                    fixedGH=manualDatafix(wdata,'GH')
                    graphdata(fixedGH,wdata,case)
                    response=prompt('Does GH need fixing? 1=yes, 0=no')

                    
            if case == 'morning':
                fixedDNI=fixedData[0]
                response=prompt('Does GH need fixing? 1=yes, 0=no')
                while(response == 1):
                        fixedGH=manualDatafix(wdata,'GH')
                        graphdata(fixedGH,wdata,case)
                        response=prompt('Does GH need fixing? 1=yes, 0=no')

                        
            if case == 'both':
               fixedDNI=fixedData[0,2]
               response=prompt('Does GH need fixing? 1=yes')
               while(response == 1):
                       fixedGH[0]=manualDatafix(wdata,'GH')
                       fixedGH[1]=manualDatafix(wdata,'GH')
                       graphdata(fixedGH,wdata,case)
                       response=prompt('Does GH need fixing? 1=yes, 0=no')

                       
                       
        if response == 3:
            if case == 'evening':
                fixedGH=fixedData[0]
                response=prompt('Does DNI need fixing? 1=yes, 0=no')
                while(response == 1):
                        fixedDNI=manualDatafix(wdata,'DNI')
                        graphdata(fixedDNI,wdata,case)
                        response=prompt('Does GH need fixing? 1=yes, 0=no')

                        
            if case == 'morning':
                fixedGH=fixedData[0]
                response=prompt('Does DNI need fixing? 1=yes, 0=no')
                while(response == 1):
                    fixedDNI=manualDatafix(wdata,'DNI')
                    graphdata(fixedDNI,wdata,case)
                    response=prompt('Does DNI need fixing? 1=yes, 0=no')

                
            if case == 'both':
               fixedGH=fixedData[0,2]
               response=prompt('Does DNI need fixing? 1=yes , 0=no')
               while(response == 1):
                   fixedDNI[0]=manualDatafix(wdata,'DNI')
                   fixedDNI[1]=manualDatafix(wdata,'DNI')
                   graphdata(fixedDNI,wdata,case)
                   response=prompt('Does DNI need fixing? 1=yes , 0=no')
                   
                   
        if response == 4:
            response = 1
            while(response == 1):
                fixedGH=manualDatafix(wdata,'GH')
                fixedDNI=manualDatafix(wdata,'DNI')
                graphdata(fixedData[fixedGH,fixedDNI],wdata,case)
                response=prompt('Are the Changes Acceptable? 1=yes, 0=no')

    temp=getTempdata(wdata)    
    newData=buildWdata(fixedDNI,fixedGH,temp)
    newData= calcDiff(newData)
    return newData
    
            
#------------------------------------------------------------------------------
    


    
    
#getfile(filedir,year)
#getjob_yr(year,century,work)