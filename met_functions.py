# -*- coding: utf-8 -*-

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
    dataGH=dataDNI=PST=[]
    
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
def manualDatafix(fixedData,wdata,case):
    dataDNI=dataGH=PST=[]    
    airmass=getAirmass(wdata)    
    for i in range (airmass[0],airmass[1]):
        dataDNI.append(wdata.loc[i,'Direct Normal [W/m^2]'])
        dataGH.append(wdata.loc[i,'Global Horiz [W/m^2]'])
        PST.append(wdata.loc[i,'PST'])
   
    tempdata=pd.DataFrame(dict(Time=PST,DataDNI=dataDNI, DataGH=dataGH))

    
    
    
    
    
    
#------------------------------------------------------------------------------
def getFixdata(date,param,model,wdata):
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
            fixedData.append(eveningDNIfix(date,param,model,wdata))
            fixedData.append(eveningGHfix(date,param,model,wdata))
            case='evening'
            
        if param[0] == 1 and param[1] == 0:
            fixedData.append(morningDNIfix(date,param,model,wdata))
            fixedData.append(morningGHfix(date,param,model,wdata))
            case='morning'         
    
        if param[0] == 1 and param[1] == 1:
            fixedData.append(morningDNIfix(date,param,model,wdata))
            fixedData.append(morningGHfix(date,param,model,wdata))
            fixedData.append(eveningDNIfix(date,param,model,wdata))
            fixedData.append(eveningGHfix(date,param,model,wdata))
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
def getModel(date,param,wdata):
    modelDNI=modelGH=modelDif=[[],[],[]] 
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
        
        
    tempdata=pd.DataFrame(dict(PST=irrtime,ModelDNI=modelDNI,DataDNI=dataDNI,ModelGH=modelGH,DataGH=dataGH,ModelDif=modelDif,DataDIFF=dataDIFF))
    #tempdata=pd.DataFrame(dict(TS=irrtime,DataDNI=dataDNI,DataGH=dataGH,DataDIFF=dataDIFF))
    tempdata.reset_index(drop=True)
    tempdata=tempdata.set_index('PST')
    #plt.gca().set_color_cycle(['black', 'red','blue'])
    tempdata.plot()



















































def getzenith(wdata):
    start=wdata.PST[wdata.PST=='14:00'].index.tolist()
    end=wdata.PST[wdata.PST=='20:00'].index.tolist()
    for ztime in range(start[0],end[0]):               
        zangle=wdata.loc[ztime,'Zenith Angle [degrees]']
        if zangle>=90:
            #z_end=wdata.loc[ztime,'PST']
            zenith_time=[start[0],ztime] #pass back index values for the start and end zenith times            
            return zenith_time
    return 0







def fixGH(job_date,year,dayofyear,GH_time,wdata):
    zenith=wdata.loc[GH_time[0],'Zenith Angle [degrees]']
    GH_data=wdata[['Global Horiz [W/m^2]','PST']]
    GH_work=GH_data
    if calendar.isleap(year) == True:
        year_days=366
    else:
        year_days=365
    
    measurGH_max=wdata.loc[wdata['Global Horiz [W/m^2]'].argmax(),'Global Horiz [W/m^2]']
    calcGH_max=(math.pow(math.cos((dayofyear-172)/year_days*math.pi),2)*1060+math.pow(math.sin((dayofyear-172)/year_days*math.pi),2)*560)*(1+abs(0.1152*math.pow(math.cos((dayofyear-80)/year_days*(2*math.pi)),2)))
    
    if (abs(measurGH_max-calcGH_max)>130):
        GH_max=calcGH_max
    else:
        GH_max=measurGH_max
    
    if zenith > 70:
        if dayofyear >= 355 or dayofyear<= 80:        
            for time in range(GH_time[0],GH_time[1]):
                GH_work.loc[time,'Global Horiz [W/m^2]']= (math.pow(math.cos((dayofyear-80)/year_days*math.pi*2),2)*1.63605*math.pow(wdata.loc[time,'Airmass'],-1.35768)+math.pow(math.sin((dayofyear-80)/year_days*math.pi*2),2)*2.4927*math.pow(wdata.loc[time,'Airmass'],-1.26142))*GH_max        
                
        elif dayofyear > 80 and dayofyear <= 172:        
            for time in range(GH_time[0],GH_time[1]):        
                GH_work.loc[time,'Global Horiz [W/m^2]']= (math.pow(math.cos((dayofyear-80)/year_days*math.pi*2),2)*1.63605*math.pow(wdata.loc[time,'Airmass'],-1.35768)+math.pow(math.sin((dayofyear-80)/year_days*math.pi*2),2)*1.25632*math.pow(wdata.loc[time,'Airmass'],-1.31889))*GH_max        

        elif dayofyear > 172 and dayofyear <= 264:        
            for time in range(GH_time[0],GH_time[1]):
               GH_work.loc[time,'Global Horiz [W/m^2]']= (math.pow(math.cos((dayofyear-172)/year_days*math.pi*2),2)*1.25632*math.pow(wdata.loc[time,'Airmass'],-1.31889)+math.pow(math.sin((dayofyear-172)/year_days*math.pi*2),2)*1.56904*math.pow(wdata.loc[time,'Airmass'],-1.33958))*GH_max        

        elif dayofyear > 264 and dayofyear < 355:        
            for time in range(GH_time[0],GH_time[1]):
                GH_work[time]= (math.pow(math.cos((dayofyear-264)/year_days*math.pi*2),2)*1.56904*math.pow(wdata.loc[time,'Airmass'],-1.33958)+math.pow(math.sin((dayofyear-264)/year_days*math.pi*2),2)*2.4927*math.pow(wdata.loc[time,'Airmass'],-1.26142))*GH_max        
        
        y1=wdata.loc[GH_time[0],'Global Horiz [W/m^2]']/GH_work.loc[GH_work[0],'Global Horiz [W/m^2]']
        y2=wdata.loc[GH_time[1],'Global Horiz [W/m^2]']/GH_work.loc[GH_work[1],'Global Horiz [W/m^2]']
        x1=GH_time[0]
        x2=GH_time[1]
        m=getslope(x1,y1,x2,y2)
        for time in range(GH_time[0],GH_time[1]):
            m=m*(time-x1)+y1
            GH_work.loc[time,'Global Horiz [W/m^2]']=GH_work.loc[time,'Global Horiz [W/m^2]']*m
        
        GH_day=pd.concat([GH_data,GH_work], axis=1)    
        GH_day=GH_day.set_index('PST')
        plt.gca().set_color_cycle(['black', 'red'])
        GH_day.plot(title="GH Irradiance for: " + wdata.loc[1,'DATE (MM/DD/YYYY)'])
        prompt = input('Would you like to Continue?').lower()
        if prompt == 'yes':   # etc.
            return GH_work
        else:
            exit
    return 0


def getGHtime(ztime,wdata):
    print 'GH END'
    for time in range(ztime[0],ztime[1]):
                
        DirGH=wdata.loc[time,'Global Horiz [W/m^2]']-wdata.loc[time+1,'Global Horiz [W/m^2]']
        if DirGH >11:
            GH_start=time-1
            break
        else:
            GH_start=0
    print 'GH END'
    for time in range(GH_start,ztime[1]):
        DirGH=wdata.loc[time,'Global Horiz [W/m^2]']-wdata.loc[time-1,'Global Horiz [W/m^2]']
        if DirGH >15:
            GH_end=time+2
            break
        else:
            GH_end=0
    
    if GH_start == 0 or GH_end == 0:
        GH_day=wdata[['Global Horiz [W/m^2]','Direct Normal [W/m^2]','PST']]        
        GH_day=GH_day.set_index('PST')
        plt.gca().set_color_cycle(['black', 'red'])
        GH_day.plot(title="GH & Direct Normal Irradiance:")
        prompt = input('Is the data correct?').lower()
        if prompt == 'yes':
            return 0
        else:
            exit
            
    
    else:
        GH_time=[GH_start,GH_end]
        return GH_time






def get_irrstatus(job_date,param,wdata):
    modelDNI=[]
    dataDNI=[]
    modelDif=[]
    modelGH=[]    
    dataGH=[]  
    dataDIFF=[]
    dataZEN=[]
    irrtime=[]
    airmass_time=[]
    GH_change=[]
    DNI_change=[]
    DIFF_change=[]
    job_date=parser.parse(job_date)
    job_yr=job_date.year
    dayofyear=float(job_date.strftime('%j'))
    job_date=date.toordinal(job_date)
    if calendar.isleap(job_yr) == True:
        year_days=366
    else:
        year_days=365
        
    
    for time in range(0,len(wdata.index)):    
        GH_change.append(0)
        DNI_change.append(0)
        DIFF_change.append(0)
        
    Irr_changed=pd.DataFrame(dict(GH_Changed=GH_change,DNI_Changed=DNI_change,DIFF_Changed=DIFF_change))
    
    wdatatemp=pd.concat([wdata,Irr_changed], axis=1)    

    measureDNI_max=wdata.loc[wdata['Direct Normal [W/m^2]'].argmax(),'Direct Normal [W/m^2]']
    if measureDNI_max < 890:
        DNI_max=985
    else:
        DNI_max=measureDNI_max
        
    for index in range (0,1439):
        zenith=wdata.loc[index,'Zenith Angle [degrees]']
        if zenith <= 85:
            airmass_time.append(index)
            for index2 in range (index+1,1439 ):
                zenith=wdata.loc[index2,'Zenith Angle [degrees]']
                if zenith >=85:
                    airmass_time.append(index2)
                    break
            break
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
        
        
    tempdata=pd.DataFrame(dict(TS=irrtime,ModelDNI=modelDNI,DataDNI=dataDNI,ModelGH=modelGH,DataGH=dataGH,ModelDif=modelDif,DataDIFF=dataDIFF))
    #tempdata=pd.DataFrame(dict(TS=irrtime,DataDNI=dataDNI,DataGH=dataGH,DataDIFF=dataDIFF))
    tempdata.reset_index(drop=True)
    tempdata=tempdata.set_index('TS')
    #plt.gca().set_color_cycle(['black', 'red','blue'])
    tempdata.plot()
#    prompt = input('Is the data correct?').lower()
#    if prompt == 'yes':
#        return 0
#    else:
#        return 0
    mDNI_diff=[]
    mGH_diff=[]
    shading_status=[]
    ghtimestart=[]
    ghtimestop=[]
    datareturn=pd.DataFrame(dict())
    x=0
    for time in range (airmass_time[0],airmass_time[1]):
                if wdata.loc[time,'PST'] == "14:00":
                    mdiff_start=time
                    break
                x=x+1

    mdiff_end=airmass_time[1]
    print mediff_end
#    print mdiff_start
#    print x
  
    print mdiff_start
    x=0
    for time in range (mdiff_start,mdiff_end):
        
        try:
            tempdiff=modelDNI[x]-dataDNI[x]
#            print tempdiff
        except:
            break        

        mDNI_diff= modelDNI[x]-dataDNI[x]
#        print str(mDNI_diff)+" = "+str(modelDNI[x])+" - "+str(dataDNI[x])
        mGH_diff=abs(modelGH[x]-dataGH[x])
#        print str(mGH_diff)+" = "+str(modelGH[x])+" - "+str(dataGH[x])
        
        if mGH_diff>=30 and mDNI_diff<60:
            shading_status.append(1)
            y=x
#            print y-2
#            startdataGH=dataGH[y-2]
            ghtimestart.append(y-2)
            print 'y is: '+str(y)
            while(1):
                mGH_diff=abs(modelGH[y]-dataGH[y])
                    
                
                mDNI_diff= modelDNI[y]-dataDNI[y]
#                print 'y is: '+str(y)
#                print 'mGH_diff: '+str(mGH_diff)
#                print 'mDNI_diff: '+str(mDNI_diff)
                if not mGH_diff>=30 and mDNI_diff<60:
                    shading_status.append(0)                    
                    break
                y=y+1
                x=x+1
                shading_status.append(1)
#            enddataGH=dataGH[y+1]
            
#            print y+1
#            print startdataGH
#            print enddataGH
            ghtimestop.append(y+1)
            
        else:
            shading_status.append(0)
        x=x+1
            
            
            
    tempGH=tempdata['DataGH']
    tempDIFF=tempdata['DataDIFF']
    for time in range (len(ghtimestart)):
        for times in range (ghtimestart[time],ghtimestop[time]):
            fixedgh=((dataGH[ghtimestop[time]]-dataGH[ghtimestart[time]])/(ghtimestop[time]-ghtimestart[time]))*(times - ghtimestart[time])+dataGH[ghtimestart[time]]
            tempGH[times]=fixedgh
            fixeddiff=fixedgh-dataDNI[times]*math.cos((dataZEN[times])/180*math.pi)
#            print times            
#            print fixeddiff
            tempDIFF[times]=fixeddiff
    x=0
    for time in range (airmass_time[0],airmass_time[1]):
        if time == mdiff_start:
            DNImulti=dataDNI[x]/((dataGH[x]-modelDif[x])/math.cos((dataZEN[x])/180*math.pi))
            y=x
            break
        x=x+1
    
    x=0
    calcDNI=[] 
    for time in range (airmass_time[0],airmass_time[1]):
        calcDNI.append(((dataGH[x]-modelDif[x])/math.cos((dataZEN[x])/180*math.pi))*DNImulti)     
        x=x+1
        
   
    
    for time in range (y,len(calcDNI)):
        if dataZEN[time]<83:
            if (dataDNI[time]-calcDNI[time])<-60:
                print str(dataDNI[time]-calcDNI[time])
                print 'DNI trgger at:'+str(time)
            
    datareturn=pd.DataFrame(dict(TS=irrtime,DataDNI=dataDNI,DataGH=dataGH,FixedGH=tempGH,DataDiff=dataDIFF,FixedDIFF=tempDIFF,Calc_DNI=calcDNI))
    datareturn.reset_index(drop=True)
    tempsdata=datareturn    
    tempsdata.reset_index(drop=True)
    tempsdata=tempsdata.set_index('TS')
    #plt.gca().set_color_cycle(['black', 'red','blue'])
    tempsdata.plot()
    prompt = 'Is the data correct?'
    response = str(raw_input(prompt+' (y/n): ')).lower().strip()
    if response[0] == 'y': 
        i=0
        for time in range (airmass_time[0],airmass_time[1]):
            
            if not wdatatemp.loc[time,'Global Horiz [W/m^2]']==tempGH[i]:
                wdatatemp.loc[time,'Global Horiz [W/m^2]']=tempGH[i]
                wdatatemp.loc[time,'GH_Changed']=1
                wdatatemp.loc[time,'Diffuse Horiz (calc) [W/m^2]']=tempDIFF[i]                
                wdatatemp.loc[time,'DIFF_Changed']=1
            i=i+1        
    else:
        print "nope didn't do anything"
        return 0
    
    
    return wdatatemp,shading_status

    
    




def correctGH(job_date,param,wdata):
    job_date=parser.parse(job_date)
    job_yr=job_date.year
    dayofyear=float(job_date.strftime('%j'))
    job_date=date.toordinal(job_date)
    
    if param[0] == 1: #morning trigger
        print 'morning trigger'
       
        
    if param[1] == 1: #evening trigger    
        print 'evening trigger'
        ztime=getzenith(wdata)        
        if ztime ==0:
            flagerror('missing zenith data')
        GH_time=getGHtime(ztime,wdata)
        print'GH_time'        
        print GH_time
        GH_fixed=fixGH(job_date,job_yr,dayofyear,GH_time,wdata)
        print 'passed GH_fixed'
    return 0    
    
    
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



    
    
#getfile(filedir,year)
#getjob_yr(year,century,work)