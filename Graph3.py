#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 13:44:28 2020

Small static tripartite graph

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

lossAG1 = 0.10
lossAG2 = 0.20
lossAG3 = 0.40

lossBG1 = 0.10
lossBG2 = 0.20
lossBG3 = 0.40

nbunch = [{'name':'A'},
          {'name':'B'},
          {'name':'G1', 'qnode_type': 'Ground'},
          {'name':'G2', 'qnode_type': 'Ground'},
          {'name':'G3', 'qnode_type': 'Ground'},
          ]

ebunch = [{'edge': ('A', 'G1'), 'loss':lossAG1},
          {'edge': ('A', 'G2'), 'loss':lossAG2},
          {'edge': ('A', 'G3'), 'loss':lossAG3},
          {'edge': ('B', 'G1'), 'loss':lossBG1},
          {'edge': ('B', 'G2'), 'loss':lossBG2},
          {'edge': ('B', 'G3'), 'loss':lossBG3},
          ]

X.add_qnodes_from(nbunch)
X.add_qchans_from(ebunch)