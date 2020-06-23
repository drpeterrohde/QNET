#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 16:08:01 2020

Welcome traveller! This is my demo file for QNET.

QNET is intended as a high level graph-theoretical simulation of a quantum network

TODO: Summary

Please enjoy your stay and feel free to email me questions.

leoneht0@gmail.com

@author: Hudson Leone
"""
import QNET
from Graph1 import X as X1
from Graph2 import X as X2
from Graph3 import X as X3
from Graph4 import X as X4

import matplotlib.pyplot as plt

def plotPaths(G, sourceName, targetName, costType, tMax, dt):
    
    # Get Time Array
    timeArr = QNET.getTimeArr(tMax, dt)
    
    # Plot the losses of every ordinary path over time
    pathDict = QNET.getCostArrays(G, 'A', 'B', costType, tMax, dt)
    for path in pathDict:
        plt.plot(timeArr, pathDict[path], label = path.stringify())
        
    # Plot the purified loss over time.
    purArr = QNET.getPurifiedArray(G, sourceName, targetName, tMax, dt)
    plt.plot(timeArr, purArr, label = 'Purified cost')
        
    # Get the array of optimal costs over time
    optArr = QNET.getOptimalCostArray(G, sourceName, targetName, costType, tMax, dt, with_purification = True)
    line = plt.plot(timeArr, optArr, linestyle = ':', c = 'k', label = 'Optimal Path Cost')
    plt.setp(line, linewidth = 3)  
    
    plt.legend()
    plt.show()

##### DEMO #####
# Uncomment the lines of code for each test to see them in action

tMax = 10
dt = 0.1

# Test Graph 1
# plotPaths(X1, 'A', 'B', 'p', tMax, dt)

# Test Graph 2
plotPaths(X2, 'A', 'B', 'p', tMax, dt)

# Test Graph 3
# print(X3.purify('A', 'B'))

# Test Graph 4
# print(X4.purify('A', 'B'))
