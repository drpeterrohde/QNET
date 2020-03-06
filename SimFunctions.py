#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 17:25:13 2020

@author: hudson
"""

import networkx as nx
import QNET
import copy
import numpy as np
import matplotlib.pyplot as plt

def getTimeArr(tMax, dt):
    return np.arange(0, tMax, dt)

# Given the names of source and target nodes, returns a dict of arrays containing
# cost functions of every simple path from source to target from t = 0 to tMax
def getLossArrays(G, sourceName, targetName, costType, tMax, dt):
    
    # Make copy of network
    GC = copy.deepcopy(G)
    
    # get source and target from names
    source = QNET.getNode(GC, sourceName)
    target = QNET.getNode(GC, targetName)
    
    # Distribute costs of swapper nodes:
    QNET.swap(G, costType)
    
    # Create a generator of all simple paths
    simplePathGen = nx.algorithms.simple_paths.all_simple_paths(GC, source, target)
    
    # Unpack paths from generator into array
    pathArr = []
    for path in simplePathGen:
        pathArr.append(path)
    
    # Create a dictionary of paths to empty cost arrays:
    pathDict = {pathNum: [] for pathNum in range(len(pathArr))}
    
    sizeArr = tMax // dt + 1
    i = 0
    
    # Add find path cost for each simple path and add to corresponding array
    while i < sizeArr:
        j = 0
        while j < len(pathArr):
            pathCost = QNET.pathCost(GC, pathArr[j], costType)
            
            pathDict[j].append(pathCost)
            j += 1
            
        # Update satellite costs
        QNET.update(GC, dt)
        i += 1
    
    return pathDict


# Given names of source and target nodes, returns an array of optimal loss costs over time
def getOptimalLossArray(G, sourceName, targetName, costType, tMax, dt):
    
    GC = copy.deepcopy(G)
    
    # get source and target from names
    source = QNET.getNode(GC, sourceName)
    target = QNET.getNode(GC, targetName)
    
    # Initialize arrays
    lossArr = []
    sizeArr = tMax // dt + 1
    
    # Get optimal path cost and append it to costArr
    i = 0
    while i < sizeArr:
        
        loss = nx.dijkstra_path_length(GC, source, target, weight = costType)
        lossArr.append(loss)
        
        # Update satellites
        QNET.update(GC, dt)
        i += 1
    
    return lossArr

# Plots the distance between two nodes over time
def posPlot(u, v, tMax, dt):
    posArr = []
    sizeArr = tMax // dt + 1
    
    i = 0
    while i < sizeArr:
        dist = QNET.distance(u, v)
        posArr.append(dist)
        i += 1
    
    timeArr = np.arange(0, tMax, dt)
    plt.plot(timeArr, posArr)
    plt.xlabel("Time")
    plt.ylabel("Distance")
    plt.title(f"Distance between {u.name} and {v.name} over {tMax} time units")
    plt.show()