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

def getCostArr(path, costType, tMax, dt):
    """
    Calculates an array of costs for a path over a given timeframe

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
    

def getCostArrays(G, sourceName, targetName, costType, tMax, dt):
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

def getOptimalCostArray(G, sourceName, targetName, costType, tMax, dt, with_purification = True):
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

    assert costType in ['e', 'p', 'de', 'dp'], "Please choose a supported cost type from {'e', 'p', 'de', 'dp}"

    # Initialize arrays
    costArr = []
    sizeArr = tMax // dt + 1
    
    # Get optimal path cost and append it to costArr
    i = 0
    while i < sizeArr:
        
        # Get classically shortest path cost
        cost = QNET.shortest_path_length(C, sourceName, targetName, costType)
        
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

from mpl_toolkits.mplot3d import art3d

def Qnet3dPlot(Q):
    """
    Produces a static 3d plot of a Qnet graph

    Parameters
    ----------
    Q : Qnet()
        Qnet Graph

    Returns
    -------
    None.

    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Note widget requires external packkage jupyter matplotlib
    # %matplotlib widget

    for node in Q.nodes:
        x = node.coords[0]
        y = node.coords[1]
        z = node.coords[2]

        # Dictionary between colours and node types
        qnode_color = {QNET.Qnode: 'r', QNET.Ground: 'y', QNET.Swapper: 'c', QNET.Satellite: 'b'}

        ax.scatter(x, y, z, c=qnode_color[type(node)], marker='o')
        ax.text(x, y, z, '%s' % node.name, size=12, zorder=1)

        # Todo: Figure out how to offset text.

    for edge in Q.edges:
        xs = [edge[0].coords[0], edge[1].coords[0]]
        ys = [edge[0].coords[1], edge[1].coords[1]]
        zs = [edge[0].coords[2], edge[1].coords[2]]

        if (isinstance(edge[0], QNET.Satellite) or isinstance(edge[1], QNET.Satellite)):
            line = art3d.Line3D(xs, ys, zs, linestyle='--')

        else:
            line = art3d.Line3D(xs, ys, zs)

        ax.add_line(line)
    
    plt.show(fig)
    # return fig
    