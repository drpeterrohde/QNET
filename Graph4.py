#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 6 10:32:19 2020

Static tripartite graph

@author: hudson
"""

import networkx as nx
import QNET

X = QNET.Qnet()

# STATIC CHANNEL COSTS
AG1 = 0.05
AG2 = 0.10
AG3 = 0.20
AG4 = 0.25
AG5 = 0.40

BG1 = 0.05
BG2 = 0.10
BG3 = 0.20
BG4 = 0.25
BG5 = 0.40

# INITIALIZE NODES AND EDGES
nbunch = [{'name':'A'},
          {'name':'B'},
          {'name':'G1', 'qnode_type': 'Ground'},
          {'name':'G2', 'qnode_type': 'Ground'},
          {'name':'G3', 'qnode_type': 'Ground'},
          {'name':'G4', 'qnode_type': 'Ground'},
          {'name':'G5', 'qnode_type': 'Ground'},
          ]

ebunch = [{'edge': ('A', 'G1'), 'pz': AG1},
          {'edge': ('A', 'G2'), 'pz': AG2},
          {'edge': ('A', 'G3'), 'pz': AG3},
          {'edge': ('A', 'G4'), 'pz': AG4},
          {'edge': ('A', 'G5'),  'pz': AG5},
          {'edge': ('B', 'G1'), 'pz': BG1},
          {'edge': ('B', 'G2'), 'pz': BG2},
          {'edge': ('B', 'G3'), 'pz': BG3},
          {'edge': ('B', 'G4'), 'pz': BG4},
          {'edge': ('B', 'G5'),  'pz': BG5},
          ]

X.add_qnodes_from(nbunch)
X.add_qchans_from(ebunch)