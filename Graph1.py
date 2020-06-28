#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 17:11:32 2020

Linear network with one ground node and a satellite overhead

@author: hudson
"""
import QNET

X = QNET.Qnet()

Qnodes = [{'name': 'A', 'coords': [50, 0, 0]},
          {'name': 'B', 'coords': [150, 0, 0]},
          {'name': 'G', 'qnode_type': 'Ground', 'coords': [100, 0, 0]},
          {'name': 'S', 'qnode_type': 'Satellite', 'coords': [0, 0, 100], 'v_cart':[20, 0], 'range':100}]

X.add_qnodes_from(Qnodes)

Qchans = [{'edge':('A', 'G'), 'e': 0.4, 'f': 0.9},
          {'edge':('G', 'B'), 'e': 0.4, 'f': 0.9},
          {'edge':('A', 'S'), 'e': 1, 'f': 1},
          {'edge':('B', 'S'), 'e': 1, 'f': 1}]

X.add_qchans_from(Qchans)
