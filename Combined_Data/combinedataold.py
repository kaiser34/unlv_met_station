# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 15:43:51 2016

@author: admin
"""

import pandas as pd
import os





year=2006

datafile=str(year)+".csv"
origindata=pd.read_csv("../data/"+datafile)
fixeddata=pd.read_csv("../fixed/"+datafile)



