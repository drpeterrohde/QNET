#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 19:46:24 2020

@author: deepeshsingh
"""


import networkx as nx
import QNET
import numpy as np
import matplotlib.pyplot as plt
import LinearGenerator as Gen
   

def GeneratorCheck(n):
    
    
    '''
    # Graph1 deifinition using altLinGen() and then manually adding a satellite
    G = Gen.altLinGen(n, spacing = [50, 0, 0], loss = 0.15)
    
    # Add satellites to graph
    S = QNET.Satellite(name = 'S', coords = [0,0,100], velocity = [10, 10])
    G.add_node(S)
    
    nodeList = G.nodes()
    for node in nodeList:
        if type(node) != QNET.Ground and type(node) != QNET.Satellite:
            G.add_edge(node, S, loss = S.airCost(node))
            # G.add_edge(node, S2, loss = QNET.airCost(S2, node))
    '''
    
    # Equivalent Graph1 definition using altLinSatGen()
    G = Gen.altLinSatGen(n, spacing = [50,0,0], loss = 0.15, satCoord = [0,0,100], satVel = [10,10])
    
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

    # Plot optimal path cost
    line = plt.plot(timeArr, minArr, linestyle = ':', c = 'k', label = 'Optimal Path Cost')
    plt.setp(line, linewidth = 3)
    
    plt.xlabel('time')
    plt.ylabel('cost')
    plt.title('Path Costs from A to B')
    plt.legend()
    
    plt.show()
    
    
GeneratorCheck(3)
  