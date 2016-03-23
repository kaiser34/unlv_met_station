# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import os
import pandas as pd

newshade=[]
dayofyear=1
shade=pd.read_csv("shade.csv")
shade=shade.loc[shade['Date']==dayofyear]
shade=shade.reset_index(drop=True)
airmass=getAirmass(wdata) 

