#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 23:44:13 2020

@author: deepeshsingh
"""


import networkx as nx
import QNET
import numpy as np
import matplotlib.pyplot as plt
import LinearGenerator as Gen
import RegularLattice as RL
   

def RegLatCheck(x,y):
    
    # General of a Regular Lattice
    G = RL.RegLat(x,y, xspacing = [50,0,0], yspacing = [0,50,0], loss = 0.15)
    
    ''' 
    #Print Graph info
       
    for i in G.nodes:
        print(i.name, i.coords)
    for i in G.edges:
        print(i[0].name, i[1].name)
    
    G.print_qchans()
    '''
    
    # Simulate
    tMax = 10
    dt = 0.01
    
    timeArr = QNET.getTimeArr(tMax, dt)
    
    
    lossArrs = QNET.getLossArrays(G, 'A', 'B', 'loss', tMax, dt)
    minArr = QNET.getOptimalLossArray(G, 'A', 'B', 'loss', tMax, dt, with_purification=False)    

    # Plot arrays over time    
    for path in lossArrs:
        if minArr==lossArrs[path]:
            print("The optimum path is: " + path.stringify())
        plt.plot(timeArr, lossArrs[path], label = path.stringify())
        #plt.plot(timeArr, lossArrs[path])

    # Plot optimal path cost
    line = plt.plot(timeArr, minArr, linestyle = ':', c = 'k', label = 'Optimal Path Cost')
    plt.setp(line, linewidth = 3)
    
    plt.xlabel('time')
    plt.ylabel('cost')
    plt.title('Path Costs from A to B')
    plt.legend()
    
    plt.show()
    
    
RegLatCheck(3,4)  