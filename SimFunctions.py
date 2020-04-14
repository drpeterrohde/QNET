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
    """
    Make uniform array from 0 to tMax with interval dt

    Parameters
    ----------
    tMax : float
        Maximum time
    dt : float
        Time increment

    Returns
    -------
    Array

    """
    return np.arange(0, tMax, dt)


# TODO: Make get Loss Array
def getCostArr(path, costType, tMax, dt):
    """
    Calculates an array of costs for a path for a given timeframe

    Parameters
    ----------
    path : Path
        A Valid Qnet Path
    costType : str
        The type of cost you would like to calculate for
        Choose from {'loss', 'fid'}
    tMax : float
        Maximum time period
    dt : TYPE
        Time increment

    Returns
    -------
    costArr : array

    """
    costArr = []
    sizeArr = tMax // dt + 1
    i = 0
    while i < sizeArr:
        cost = path.cost(costType)
        costArr.append(cost)
        i += 1
    return costArr
    

def getLossArrays(G, sourceName, targetName, costType, tMax, dt):
    """
    Calculates an array of costs for all simple paths for a given timeframe

    Parameters
    ----------
    G : Qnet()
        Qnet graph
    sourceName : str
        Name of source node
    targetName : str
        Name of target node
    costType : str
        The type of cost you would like to calculate for
        Choose from {'loss', 'fid'}
    tMax : float
        Maximum time period
    dt : TYPE
        Time increment

    Returns
    -------
    pathDict : dict
        Dictionary of paths to their cost in units of costType

    """
    
    C = copy.deepcopy(G)
    
    # get source and target from names
    source = C.getNode(sourceName)
    target = C.getNode(targetName)
    
    # Create a generator of all simple paths
    simplePathGen = nx.algorithms.simple_paths.all_simple_paths(C, source, target)
    
    # Unpack paths from generator into array as QNET paths
    pathArr = []
    for path in simplePathGen:
        pathArr.append(QNET.Path(C, path))
        
    # Assign each path to an empty cost array
    pathDict = {path: [] for path in pathArr}
    
    # Initialize array size
    sizeArr = tMax // dt + 1
    i = 0    
    
    while i < sizeArr:
        j = 0
        while j < len(pathArr):
            # Get the cost of each path and append it to respective array
            pathCost = pathArr[j].cost(costType)
            pathDict[pathArr[j]].append(pathCost)
            j += 1
            
        C.update(dt)
        i += 1
    
    return pathDict

def getOptimalLossArray(G, sourceName, targetName, costType, tMax, dt, with_purification = True):
    """
    Calculate the costs of the lowest cost path from "source" to "target" over time

    Parameters
    ----------
    G : Qnet()
        Qnet graph
    sourceName : str
        Name of source node
    targetName : str
        Name of target node
    costType : str
        The type of cost you would like to calculate for
        Choose from {'loss', 'fid'}
    tMax : float
        Maximum time period
    dt : TYPE
        Time increment

    Returns
    -------
    optLossArr : array

    """
    
    C = copy.deepcopy(G)
    
    # get source and target from names
    source = C.getNode(sourceName)
    target = C.getNode(targetName)
    
    # Initialize arrays
    lossArr = []
    sizeArr = tMax // dt + 1
    
    # Get optimal path cost and append it to costArr
    i = 0
    while i < sizeArr:
        
        # Get classically shortest path cost
        loss = nx.dijkstra_path_length(C, source, target, QNET.weight)
        
        # Get purified cost
        pur_loss = C.purify(sourceName, targetName)
        
        # Compare costs, add the lower of the two:
        if with_purification:
            if loss < pur_loss:
                lossArr.append(loss)
            else:
                lossArr.append(pur_loss)
        else:
            lossArr.append(loss)
        
        # Update satellites
        C.update(dt)
        i += 1
    
    return lossArr

def getPurifiedArray(G, sourceName, targetName, costType, tMax, dt):
    """
    Calculate the costs of an entanglement purification from "source" to "target" over time

    Parameters
    ----------
    G : Qnet()
        Qnet graph
    sourceName : str
        Name of sourceNode
    targetName : str
        Name of targetNode
    costType : str
        The type of cost you would like to calculate for
        Choose from {'loss', 'fid'}
    tMax : float
        Maximum time period
    dt : TYPE
        Time increment

    Returns
    -------
    purLossArr : array

    """
    
    C = copy.deepcopy(G)
    
    # Initialize arrays
    lossArr = []
    sizeArr = tMax // dt + 1
    
    # Get purified path cost and append it to costArr
    i = 0
    while i < sizeArr:
        
        # Get purified fidelity from purify
        loss = C.purify(sourceName, targetName)
        
        # Convert to loss
        lossArr.append(loss)
        
        # Update satellites
        C.update(dt)
        i += 1
    
    return lossArr

def posPlot(u, v, tMax, dt):
    """
    Plot the distance between two nodes over time
    """
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

    