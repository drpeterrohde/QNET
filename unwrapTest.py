#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 15:05:05 2020

@author: hudson
"""

import QNET
import matplotlib.pyplot as plt
import networkx as nx
import copy
import numpy as np
import random

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

#### TEST FUNCTIONS ####
def unwrapTest():
    mydict = QNET.unwrap(X, 'A', 'B', 'loss')

    #debug
    print('\n')
    for path in mydict:
        for node in path:
            print(node)
        print('\n')

# TODO Test purify
def purifyTest():
    print(QNET.purify(X, 'A', 'B', 'loss'))
    

#### MAIN ####
    
purifyTest()

"""    
# TODO:
# Test on large complete graph with randomly generated weights:

K = nx.complete_graph(100)

i = 0
for node in K.nodes():
    newNode = QNET.Qnode(name = i)
    K.add_node(newNode)
    i += 1

# Add weights to each edge:

for edge in K.edges():
    K.add_edge(edge[0], edge[1], loss = random.randint(1,11))


# QNET.unwrap(K, '0', '99', 'loss')



#compleX = nx.Graph()
#compleX.add_nodes_from(np.arange(1,101))
"""

