#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 10:32:19 2020

Static tripartite graph

@author: hudson
"""

import networkx as nx
import QNET

X = QNET.Qnet()

# STATIC CHANNEL COSTS
# Loss of 0.05 corresponds to ~95% success probability
# 0.20 ~ 80% success probability
# 0.69 ~ 50% success probability

# Any path below 50% success probability should __NOT__ be purified

lossAG1 = 0.05
lossAG2 = 0.10
lossAG3 = 0.20
lossAG4 = 0.25
lossAG5 = 0.40

lossBG1 = 0.05
lossBG2 = 0.10
lossBG3 = 0.20
lossBG4 = 0.25
lossBG5 = 0.40

nbunch = [{'name':'A'},
          {'name':'B'},
          {'name':'G1', 'qnode_type': 'Ground'},
          {'name':'G2', 'qnode_type': 'Ground'},
          {'name':'G3', 'qnode_type': 'Ground'},
          {'name':'G4', 'qnode_type': 'Ground'},
          {'name':'G5', 'qnode_type': 'Ground'},
          ]

ebunch = [{'edge': ('A', 'G1'), 'loss':lossAG1},
          {'edge': ('A', 'G2'), 'loss':lossAG2},
          {'edge': ('A', 'G3'), 'loss':lossAG3},
          {'edge': ('A', 'G4'), 'loss':lossAG4},
          {'edge': ('A', 'G5'),  'loss':lossAG5},
          {'edge': ('B', 'G1'), 'loss':lossBG1},
          {'edge': ('B', 'G2'), 'loss':lossBG2},
          {'edge': ('B', 'G3'), 'loss':lossBG3},
          {'edge': ('B', 'G4'), 'loss':lossBG4},
          {'edge': ('B', 'G5'),  'loss':lossBG5},
          ]

X.add_qnodes_from(nbunch)
X.add_qchans_from(ebunch)