#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 13:44:28 2020

Small static tripartite graph without node costs

@author: hudson
"""

import networkx as nx
import QNET

X = QNET.Qnet()

nbunch = [{'name':'A'},
          {'name':'B'},
          {'name':'G1', 'qnode_type': 'Ground'},
          {'name':'G2', 'qnode_type': 'Ground'},
          {'name':'G3', 'qnode_type': 'Ground'}]

ebunch = [{'edge': ('A', 'G1'), 'e': 0.9, 'f': 0.9},
          {'edge': ('A', 'G2'), 'e': 0.8, 'f': 0.8},
          {'edge': ('A', 'G3'), 'e': 0.7, 'f': 0.7},
          {'edge': ('B', 'G1'), 'e': 0.9, 'f': 0.9},
          {'edge': ('B', 'G2'), 'e': 0.8, 'f': 0.8},
          {'edge': ('B', 'G3'), 'e': 0.7, 'f': 0.7}]

X.add_qnodes_from(nbunch)
X.add_qchans_from(ebunch)