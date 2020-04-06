#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 17:11:32 2020

Linear network with one ground node and a satellite overhead

@author: hudson
"""

import QNET

# Node positions:
posA = [50,0,0]
posG = [100, 0, 0]
posB = [150, 0, 0]

# Satellite positions and initial Velocities:
posS = [0,0,100]
vsat = [20, 0]

# STATIC CHANNEL LOSSES
lossAG = 0.2
lossGB = 0.2

####### INITIALIZATIONS #######

# Initialise Network and Nodes
X = QNET.Qnet()

Qnodes = [{'name': 'A', 'coords': posA},
          {'name': 'B', 'coords': posB},
          {'name': 'G', 'qnode_type':'Ground', 'coords': posG},
          {'name': 'S', 'qnode_type':'Satellite', 'coords': posS, 'velocity':vsat},
          ]

X.add_qnodes_from(Qnodes)

# Initial satellite losses
lossAS = (X.getNode('S')).airCost(X.getNode('A'))
lossBS = (X.getNode('S')).airCost(X.getNode('B'))

Qchans = [{'edge':('A','G'),'loss':lossAG},
          {'edge':('G','B'),'loss':lossGB},
          {'edge':('A','S'),'loss':lossAS},
          {'edge':('B','S'),'loss':lossBS},
          ]

# (X.getNode('S')).airCost(X.getNode('B')

X.add_qchans_from(Qchans)