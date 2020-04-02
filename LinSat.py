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
import networkx as nx
import QNET
import matplotlib.pyplot as plt

######## USER INPUTS ########

# Node positions:
posA = [50,0,0]
posG = [100, 0, 0]
posB = [150, 0, 0]

# Satellite positions and initial Velocities:
posS = [0,0,100]
vsat = [20, 0]

# STATIC CHANNEL LOSSES
lossAG = 16
lossGB = 16

# MAX TIME AND RESOLUTION
tMax = 10
dt = 0.1

####### INITIALIZATIONS #######

# Initialise Network and Nodes
X = nx.Graph()

# Create qnet nodes and add them to graph as nodes
A = QNET.Qnode('A', posA)
B = QNET.Qnode('B', posB)
G = QNET.Qnode('G', posG)

X.add_nodes_from([A, B, G])

# Create satellite and add to graph as node:
S = QNET.Satellite('S', posS, vsat)
X.add_node(S)

# Add edges
X.add_edge(A,G, loss = lossAG)
X.add_edge(G,B, loss = lossGB)
X.add_edge(A,S, loss = QNET.airCost(A, S))
X.add_edge(S,B, loss = QNET.airCost(S, B))


######## MAIN ########

# Get loss arrays:
lossArrays = QNET.getLossArrays(X, 'A', 'B', 'loss', tMax, dt)
optLossArr = QNET.getOptimalLossArray(X, 'A', 'B', 'loss', tMax, dt)

# Get time array:
timeArr = QNET.getTimeArr(tMax, dt)

plt.plot(timeArr, lossArrays[0])
plt.plot(timeArr, lossArrays[1])
 
# Plot optimal cost:
line = plt.plot(timeArr, optLossArr, linestyle = ':', c = 'k', label = 'Optimal Path Cost')
plt.setp(line, linewidth = 3)

# LABEL GRAPHS
plt.xlabel('time')
plt.ylabel('cost')
plt.title('Optimal path cost from A to B with moving satellite')
# plt.legend()
plt.show()

##### DEBUGGING #####
mysteryNode = QNET.getNode(X, 'A')
assert(A == mysteryNode)
    


