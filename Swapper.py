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
import matplotlib.pyplot as plt
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
vSat = [30, 0]

# STATIC CHANNEL LOSSES
lossAG1 = 10
lossG1T = 10
lossTG2 = 10
lossG2B = 10

# MAX TIME AND RESOLUTION
tMax = 10
dt = 0.1

####### INITIALIZATIONS #######


# INITIALIZE NETWORK AND NODES
X = nx.Graph()

# Alternative strategy:
"""
nodeBunch = [('A', posA),
             ('B', posB),
             ('Ground', 'G1', posG1),
             ('Ground', 'G2', posG2),
             ('Swapper', 'T', posT),
             ('Satellite', 'S', posS, vSat)]

nodeArray = QNET.makeQnodes(nodeBunch)
X.add_nodes_from(nodeArray)
"""

# debug
A = QNET.Qnode('A', posA)
B = QNET.Qnode('B', posB)
G1 = QNET.Ground('G1', posG1)
G2 = QNET.Ground('G2', posG2)
T = QNET.Swapper('T', posT)
S = QNET.Satellite('S', posS, vSat) # (vx, vy, name, coordinates)


# ADD NODES TO NETWORK
nodeList = [A, B, G1, G2, T, S]
X.add_nodes_from(nodeList)

# INITIALIZE CHANNELS
ebunch = [(A, G1, {'loss':lossAG1}),
          (G1, T, {'loss':lossG1T}),
          (T, G2, {'loss':lossTG2}),
          (G2, B, {'loss':lossG2B}),
          (A, S, {'loss': QNET.airCost(A, S)}),
          (S, T, {'loss': QNET.airCost(S, T)}),
          (S, B, {'loss': QNET.airCost(S, B)})]

X.add_edges_from(ebunch)

######## MAIN ########

# GENERATE ARRAYS
timeArr = QNET.getTimeArr(tMax, dt)
lossArrays = QNET.getLossArrays(X, 'A', 'B', 'loss', tMax, dt)
optLossArr = QNET.getOptimalLossArray(X, 'A', 'B', 'loss', tMax, dt)

# Plot arrays over time
i = 0
while i < len(lossArrays):
    plt.plot(timeArr, lossArrays[i], label = f'Path {i}')
    i += 1

# Plot optimal path cost
line = plt.plot(timeArr, optLossArr, linestyle = ':', c = 'k', label = 'Optimal Path Cost')
plt.setp(line, linewidth = 3)

# LABEL GRAPHS
plt.xlabel('time')
plt.ylabel('cost')
plt.title('Path Costs from A to B')

plt.legend()
plt.show()

##### DEBUGGING #####
