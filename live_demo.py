#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 18:49:24 2020

This is code for a live demo I'm conducting on April 18th 2020.
The objective here is to build a network of three different paths
between A and B (One of which will include a satellite) and perform
an entanglement purification

@author: hudson
"""

# Imports
import networkx as nx
import QNET
import matplotlib.pyplot as plt

# TODO:
# Create empty Qnet:
Q = QNET.Qnet()

node_bunch = [
    {'name':'A', 'coords':[0,0,0]},
    {'name':'G1', 'qnode_type':'Ground', 'coords':[10,0,0]},
    {'name':'T', 'qnode_type':'Swapper', 'coords':[20,0,0]},
    {'name':'G2', 'qnode_type':'Ground', 'coords':[30,0,0]},
    {'name':'B', 'coords':[40,0,0]},
    {'name':'S', 'qnode_type':'Satellite', 'coords':[0,0,100], 'velocity':[25,25]}
    ]

Q.add_qnodes_from(node_bunch)

for node in Q.nodes:
    print(node)

# TODO:
# Initialize qchans with QNET. add_qchans_from

ebunch = [{'edge': ('A', 'G1'), 'loss':0.5},
          {'edge': ('G1', 'T'), 'loss':0.5},
          {'edge': ('T', 'G2'), 'loss':0.5},
          {'edge': ('G2', 'B'), 'loss':0.5},
          {'edge': ('S', 'A'), 'loss':0},
          {'edge': ('S', 'B'), 'loss':0}, 
          ]

Q.add_qchans_from(ebunch)
print('\n')
Q.print_qchans()

# Get all of the paths with nx.all_simple_paths
generator = nx.all_simple_paths(Q, Q.getNode('A'), Q.getNode('B'))

path_array = []
for item in generator:
    new_path = QNET.Path(Q, item)
    path_array.append(new_path)
    
# print(path_array)

# Make time array with QNET.getTimeArray
tMax = 10
dt = 0.01
timeArr = QNET.getTimeArr(tMax, dt)

# Get Shortest path array with QNET.getOptimalLossArray
# (Remembering to set with_purification = False)
optLossArr = QNET.getOptimalLossArray(Q, 'A', 'B', 'loss', tMax, dt, with_purification = False)

# QNET.getLossArrays not working
CostDict = QNET.getLossArrays(Q, 'A', 'B', 'loss', tMax, dt)
for arr in CostDict.values():
    plt.plot(timeArr, arr)

plt.plot(timeArr, optLossArr)
plt.show()

# TODO:
# Get Purified array with QNET.getPurifiedArray

# TODO:
# Plot costs with time, hopefully purified array will be lower cost!