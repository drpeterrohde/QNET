#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 16:55:15 2020

This code considers the following linear network:
    
    ##-S-##

A -- G1 -- T -- G2 -- B

Where A and B are the target nodes, G1, G2 are ground stations, T is an
entanglement swapper and S is a satellite node moving at constant velocity

At any given moment in time let S be connected to A, T, and B. S itself
is a producer of bell pairs.

@author: hudson
"""
import QNET
from Node import Node
from Node import Ground
from Node import Satellite
from Node import Swapper
from Network import Network
from Channel import Channel
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import copy

######## USER INPUTS #########

# Node positions:
posA = [50,0,0]
posG1 = [100, 0, 0]
posT = [150, 0, 0]
posG2 = [200, 0, 0]
posB = [250, 0, 0]


# Satellite positions and initial Velocities:
posS = [0,0,100]
vx = 30
vy = 0

# STATIC CHANNEL LOSSES
lossAG1 = 12
lossG1T = 12
lossTG2 = 12
lossG2B = 12

# MAX TIME AND RESOLUTION
tMax = 10
dt = 0.1

####### FUNCTIONS #######

def getTimeArr(tMax, dt):
    return np.arange(0, tMax, dt)

# Returns an array of optimal loss costs over time
def getOptimalLossArray(N, sourceName, targetName, tMax, dt):
    
    # Make copy of network:
    NC = copy.deepcopy(N)
    
    # Distribute cost from T
    NC.swap()
    
    # Initialise arrays
    lossArr = []
    sizeArr = tMax // dt + 1
    
    # Initialise satellite channel
    NC.updateSatChannels()
    
    # Define paths: (TODO: Find way to automate this)
    list1 = ['A', 'G1', 'T', 'G2', 'B']
    list2 = ['A', 'S', 'T', 'G2', 'B']
    list3 = ['A', 'G1', 'T', 'S', 'B']
    
    i = 0
    while i < sizeArr:
        
        # Calculate optimal path cost and append it to costArr:
        #X = QNET.q2x(NC)
        #loss = nx.dijkstra_path_length(X, sourceName, targetName, weight = 'loss')
        
        path1 = NC.getChanPathFromList(list1)
        path2 = NC.getChanPathFromList(list2)
        path3 = NC.getChanPathFromList(list3)
        
        pathCost1 = NC.pathCost(path1, 'loss')
        pathCost2 = NC.pathCost(path2, 'loss')
        pathCost3 = NC.pathCost(path3, 'loss')
        
        lossArr.append(min([pathCost1, pathCost2, pathCost3]))
        
        # Update satellite position
        NC.updateSatPos(dt)

        # Update satellite cost channels
        NC.updateSatChannels()
        
        i += 1
    
    return lossArr


# Returns an array of a given path over time
# I.E. source -> satellite -> target
def getLossArray(N, nodeList, costType, tMax, dt):
    
    # Make copy of network
    NC = copy.deepcopy(N) 
    chanPath = NC.getChanPathFromList(nodeList)
    
    # Distribute cost from T
    NC.swap()
    
    # Initialise arrays:
    lossArr = []
    sizeArr = tMax // dt + 1

    # Initialize satellite
    NC.updateSatChannels()
    
    i = 0
    while i < sizeArr:
        
        totalLoss = NC.pathCost(chanPath, 'loss')
        lossArr.append(totalLoss)
        
        # Update satellite position
        NC.updateSatPos(dt)
        
        # TEST: Update satellite costs from Network:
        NC.updateSatChannels()
        
        i += 1
        
    return lossArr
        

# Plots the distance of the satellite to a given node over time
def posPlot(N, sat, target, tMax, dt):
    posArr = []
    sizeArr = tMax // dt + 1
    i = 0
    while i < sizeArr:
        
        # Update position and append it to posArr
        sat.posUpdate(dt)
        pos = sat.distance(target)
        posArr.append(pos)
        
        i += 1
    
    timeArr = np.arange(0, dt*(sizeArr), dt)
    plt.plot(timeArr, posArr)
    plt.xlabel("Time")
    plt.ylabel("Distance")
    plt.title(f"Distance between satellite and {target.name}")
    plt.show()


# getPathFromList constructs a list of nodes from network N specified by a List
# Useful for obtaining paths, however it does NOT check if the path is valid
# Will warn user if one or more nodes in list does not exist in N.
def getNodesFromList(N, List):
    nodes = []
    for name in List:
        nodeExists = False
        for node in N.nodes:
            if node.name == name:
                nodes.append(node)
                nodeExists = True
        if nodeExists == False:
            print("Warning! One or more nodes in list does not exist!")
    return nodes

####### INITIALIZATIONS #######


# INITIALIZE NETWORK AND NODES
N = Network()

A = Node('A', posA)
B = Node('B', posB)
G1 = Ground('G1', posG1)
G2 = Ground('G2', posG2)
T = Swapper('T', posT)
S = Satellite(vx, vy, 'S', posS) # (vx, vy, name, coordinates)

# ADD NODES TO NETWORK
nodeList = [A, B, G1, G2, T, S]

for node in nodeList:
    N.addNode(node)

# INITIALIZE CHANNELS
chAG1 = Channel(source = A, dest = G1)
chG1T = Channel(source = G1, dest = T)
chTG2 = Channel(source = T, dest = G2)
chG2B = Channel(source = G2, dest = B)
chSA = Channel(source = S, dest = A)
chST = Channel(source = S, dest = T)
chSB = Channel(source = S, dest = B)

channelList = [chAG1, chG1T, chTG2, chG2B, chSA, chST, chSB]

# ADD CHANNELS TO NETWORK
for channel in channelList:
    N.addChannel(channel)


# ADD COSTS TO STATIC CHANNELS
chAG1.setCost('loss', lossAG1)
chG1T.setCost('loss', lossG1T)
chTG2.setCost('loss', lossTG2)
chG2B.setCost('loss', lossG2B)

# ADD INITIAL COST TO SATELLITE CHANNELS
N.updateSatChannels()


######## MAIN ########

# INITIALIZE PATHS
path1 = ['A', 'G1', 'T', 'G2', 'B']
path2 = ['A', 'S', 'T', 'G2', 'B']
path3 = ['A', 'G1', 'T', 'S', 'B']

# GENERATE ARRAYS
timeArr = getTimeArr(tMax, dt)


lossArr1 = getLossArray(N, path1, 'loss', tMax, dt)
lossArr2 = getLossArray(N, path2, 'loss', tMax, dt)
lossArr3 = getLossArray(N, path3, 'loss', tMax, dt)
optLossArr = getOptimalLossArray(N, 'A', 'B', tMax, dt)


plt.plot(timeArr, lossArr1, label = 'Cost of path A--T--B')
plt.plot(timeArr, lossArr2, label = 'Cost of path A--S--T--B')
plt.plot(timeArr, lossArr3, label = 'Cost of path A--T--S--B')

line = plt.plot(timeArr, optLossArr, linestyle = ':', c = 'k', label = 'Optimal Path Cost')
plt.setp(line, linewidth = 3)

# LABEL GRAPHS
plt.xlabel('time')
plt.ylabel('cost')
plt.title('Path Costs from A to B')

plt.legend()
plt.show()

##### DEBUGGING #####
# TEST NETWORK COPY

#print(nodeChan.dest)
#print(nodeChan.dest)
