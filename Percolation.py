#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  2 15:28:36 2020

@author: deepeshsingh
"""

import networkx as nx
import QNET
import random
import copy

def defectedGraph(G, prob):
    '''
    Constructs a defected graph using the given probaility. 

    Parameters
    ----------
    G : QNET Graph
        Graph on which defects are introduced.
    prob : float
         Probability of occupation of a single site.

    Returns
    -------
    Q : QNET graph
        Defected graph constructed from G.

    '''
    
    Q = copy.deepcopy(G)
    
    for node in list(G.nodes)[1:-1]:
        p = random.random()
        if p>prob:
            dummyNode = Q.getNode(node.name)
            Q.remove_node(dummyNode)
    
    return Q

  
