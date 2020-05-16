#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 14:09:24 2020

Linear network with two ground nodes, a swapper node, and one satellite

@author: hudson
"""

import networkx as nx
import QNET
from Qgraph import Qnet

######## USER INPUTS #########

# Node positions:
posA = [50,0,0]
posG1 = [100, 0, 0]
posT = [150, 0, 0]
posG2 = [200, 0, 0]
posB = [250, 0, 0]

# Satellite arguements
posS = [0,0,100]
vSat = [30, 0]
range = 100

# STATIC CHANNEL COSTS
# Loss of 0.05 corresponds to ~95% success probability
A_G1_pz = 0.05
G1_T_pz = 0.05
T_G2_pz = 0.05
G2_B_pz = 0.05

####### INITIALIZATIONS #######

# INITIALIZE NETWORK AND NODES
X = Qnet()

nbunch = [{'name':'A', 'coords': posA},
          {'name':'B', 'coords': posB},
          {'name':'G1', 'coords': posG1, 'qnode_type':'Ground'},
          {'name':'G2', 'coords': posG2, 'qnode_type': 'Ground'},
          {'name':'T', 'coords': posT, 'qnode_type': 'Swapper'},
          {'name':'S', 'coords': posS, 'qnode_type': 'Satellite', 'velocity':vSat, 'range':range},
          ]

X.add_qnodes_from(nbunch)

ebunch = [{'edge': ('A', 'G1'), 'pz': A_G1_pz},
          {'edge': ('G1', 'T'), 'pz': G1_T_pz},
          {'edge': ('T', 'G2'), 'pz': T_G2_pz},
          {'edge': ('G2', 'B'), 'pz': G2_B_pz},
          {'edge': ('S', 'A')},
          {'edge': ('S', 'B')}
          ]

X.add_qchans_from(ebunch)