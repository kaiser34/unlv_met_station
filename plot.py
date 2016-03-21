# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 16:55:31 2016

@author: admin
"""
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.tools as tls
# Create random data with numpy
import numpy as np

tls.set_credentials_file(username='goomer13', api_key='k22jyhm9w2')



N = 100
random_x = np.linspace(0, 1, N)
random_y0 = np.random.randn(N)+5
random_y1 = np.random.randn(N)
random_y2 = np.random.randn(N)-5

# Create traces
trace0 = go.Scatter(
    x = random_x,
    y = random_y0,
    mode = 'lines',
    name = 'lines'
)
trace1 = go.Scatter(
    x = random_x,
    y = random_y1,
    mode = 'lines+markers',
    name = 'lines+markers'
)
trace2 = go.Scatter(
    x = random_x,
    y = random_y2,
    mode = 'markers',
    name = 'markers'
)
data = [trace0, trace1, trace2]

# Plot and embed in ipython notebook!
py.iplot(data, filename='line-mode')