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

# Satellite arguements:
posS = [0,0,100]
vsat = [20, 0]
range = 100

# STATIC CHANNEL COSTS
AG_pz = 0.15
GB_pz = 0.15

####### INITIALIZATIONS #######

# Initialise Network and Nodes
X = QNET.Qnet()

Qnodes = [{'name': 'A', 'coords': posA},
          {'name': 'B', 'coords': posB},
          {'name': 'G', 'qnode_type':'Ground', 'coords': posG},
          {'name': 'S', 'qnode_type':'Satellite', 'coords': posS, 'v_cart':vsat, 'range':range},
          ]

X.add_qnodes_from(Qnodes)

Qchans = [{'edge':('A','G'),'e':0.4, 'pz':AG_pz},
          {'edge':('G','B'),'e':0.4, 'pz':GB_pz},
          {'edge':('A','S')},
          {'edge':('B','S')},
          ]

X.add_qchans_from(Qchans)