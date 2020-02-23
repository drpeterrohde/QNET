#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 16:55:15 2020

This code considers a flat plane with three ground nodes (G, A, B)
and one satellite node (S). The ground nodes are stationary while 
the satellite tracks overhead with some constant velocity.

G produces a bell pair and sends each component of that pair to A and B.
The goal is to reduce the fidelity cost function of the transportation
by as much as possible.

@author: hudson
"""
import QNET
from Node import Node
from Node import Satellite
from Network import Network
from Channel import Channel
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

######## USER INPUTS ########

# Node positions:
posA = [0,0,0]
posG = [100, 0, 0]
posB = [200, 0, 0]


# Satellite positions and initial Velocities:
posS = [0,0,100]
vx = 20
vy = 0

# STATIC CHANNEL LOSSES
lossAG = 15
lossGB = 15

# MAX TIME AND RESOLUTION
tMax = 10
dt = 0.1

####### FUNCTIONS #######

def getTimeArr(tMax, dt):
    return np.arange(0, tMax, dt)

# Returns an array of optimal loss costs over time
def getOptimalLossArray(N, S, source, target, tMax, dt):
    
    # Remember initial satellite position
    initx = S.coords[0]
    inity = S.coords[1]
    initz = S.coords[2]
    
    # Initialise arrays
    lossArr = []
    sizeArr = tMax // dt + 1
    
    # Initialise satellite channel
    S.updateChannels()
    
    i = 0
    while i < sizeArr:
        
        # Calculate optimal path cost and append it to costArr:
        X = QNET.q2x(N)
        loss = nx.dijkstra_path_length(X, source.name, target.name, weight = 'loss')
        lossArr.append(loss)
        
        # Update satellite position
        S.posUpdate(dt)
        
        # Update satellite channels
        S.updateChannels()
        
        i += 1
    
    # Return satellite back to original position
    S.coords[0] = initx
    S.coords[1] = inity
    S.coords[2] = initz
    
    return lossArr

# Returns an array of a satellite path over time
# I.E. source -> satellite -> target
def getLossArray(N, S, source, target, tMax, dt):
    
    # Remember initial satellite position
    initx = S.coords[0]
    inity = S.coords[1]
    initz = S.coords[2]
    
    # Initialise arrays:
    lossArr = []
    sizeArr = tMax // dt + 1
    
    i = 0
    while i < sizeArr:
        # Debug
        sourceLoss = S.costFunc(source)
        targetLoss = S.costFunc(target)
        
        totalLoss = sourceLoss + targetLoss
        lossArr.append(totalLoss)
        
        # Update satellite position
        S.posUpdate(dt)
        
        i += 1
    
    # Return satellite back to original position
    S.coords[0] = initx
    S.coords[1] = inity
    S.coords[2] = initz
    
    return lossArr
        

# Plots the distance of the satellite to a given node over time
def posPlot(N, sat, target, sizeArr, dt):
    posArr = []
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
    
    

####### INITIALIZATIONS #######

# Initialise Network and Nodes
N = Network()
A = Node('A', posA)
B = Node('B', posB)
G = Node('G', posG)

# Add nodes to network
N.addNode(A)
N.addNode(B)
N.addNode(G)

#  ADD SATELLITE
# (height, vx, vy, name, coordinates)
S = Satellite(vx, vy, 'Tesla Roadster', posS)
N.addNode(S)

# INITIALIZE CHANNELS
chAG = Channel(source = A, dest = G)
chGB = Channel(source = G, dest = B)
chAS = Channel(source = A, dest = S)
chBS = Channel(source = B, dest = S)

# ADD CHANNELS TO NETWORK
N.addChannel(chAG)
N.addChannel(chGB)
N.addChannel(chAS)
N.addChannel(chBS)

# ADD COSTS TO STATIC CHANNELS
chAG.setCost('loss', lossAG)
chGB.setCost('loss', lossGB)

# ADD INITIAL COST TO SATELLITE CHANNELS
chAS.setCost('loss', S.costFunc(A))
chAS.setCost('loss', S.costFunc(B))


# TEST SATELLITE NODE UPDATES
# N.printNodes()


######## MAIN ########

timeArr = getTimeArr(tMax, dt)
optLossArr = getOptimalLossArray(N, S, A, B, tMax, dt)
LossArr = getLossArray(N, S, A, B, tMax, dt)

# PLOT CONSTANT COST FUNCTION FOR GB CHANNEL
staticCostArr = (lossAG + lossGB) * np.ones(len(timeArr))
plt.plot(timeArr, staticCostArr, label = 'Cost of path AB')

# PLOT COST FUNCTION FOR GSB CHANNEL
plt.plot(timeArr, LossArr, label = 'Cost of path ASB')
 
# PLOT OPTIMAL COST FUNCTION FROM G TO B
line = plt.plot(timeArr, optLossArr, linestyle = ':', c = 'k', label = 'Optimal Path Cost')
plt.setp(line, linewidth = 3)

# LABEL GRAPHS
plt.xlabel('time')
plt.ylabel('cost')
plt.title('Optimal path cost from A to B with moving satellite')
plt.legend()
plt.show()


##### DEBUGGING #####
# print(LossArr)
    


