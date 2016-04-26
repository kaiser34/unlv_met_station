# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 13:59:58 2016

@author: Aaron Sahm
"""


dataDNI=[]
dataGH=[]
PST=[]
position=[]
airmass=getAirmass(wdata)    
for i in range (airmass[0],airmass[1]):
    dataDNI.append(wdata.loc[i,'Direct Normal [W/m^2]'])
    dataGH.append(wdata.loc[i,'Global Horiz [W/m^2]'])
    PST.append(wdata.loc[i,'PST'])

tempdata=pd.DataFrame(dict(Time=PST,DataDNI=dataDNI, DataGH=dataGH))

position=[]


    
def on_press(event):
    if fig.canvas.manager.toolbar._active is None:
        print('you pressed', event.button, event.xdata, event.ydata)
        position.append(int(round(event.xdata,0)))


fig, ax = plt.subplots()
tolerance = tempdata.index[len(tempdata)-1]+1 # points
ax.plot(tempdata.index,tempdata.loc[:,'DataDNI'],tempdata.index,tempdata.loc[:,'DataGH'], picker=tolerance)
plt.waitforbuttonpress()
dips = int(prompt('How many dips are there?'))
x=0
while len(position)<(dips*2):
    fig.canvas.mpl_connect('button_press_event', on_press)
    plt.waitforbuttonpress()
    if plt.waitforbuttonpress(): 
        plt.close()        
        break

plt.close()

position=[]
airmass=getAirmass(wdata)    
  
tempdata=pd.DataFrame(dict(Time=modelData.loc[:,'PST'],DataDNI=modelData.loc[:,'DataDNI'], DataGH=modelData.loc[:,'DataGH']))
fig, ax = plt.subplots()
tolerance = tempdata.index[len(tempdata)-1]+1 # points
ax.plot(tempdata.index,tempdata.loc[:,'DataDNI'],tempdata.index,tempdata.loc[:,'DataGH'], picker=tolerance)
plt.waitforbuttonpress()
dips = int(prompt('How many dips are there?'))
while len(position)<(dips*2):
    fig.canvas.mpl_connect('button_press_event', on_press)
    plt.waitforbuttonpress()
    if plt.waitforbuttonpress(): 
        plt.close()        
        break

plt.close()