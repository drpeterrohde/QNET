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

def defectedGraph(G, pThresh):
    Q = copy.deepcopy(G)
    
    for node in list(G.nodes)[1:-1]:
        p = random.random()
        if p>pThresh:
            dummyNode = Q.getNode(node.name)
            Q.remove_node(dummyNode)
        
    #tMax = 10
    #dt = 0.01    
    pathExists = 0
    #lossArr = []
    lossArrValue = 0
    #fidArr = []
    fidArrValue = 0
    
    
    try: 
        # Slow alternative to check if path exists 
        #lossArr = QNET.getOptimalLossArray(Q, 'A', 'B', 'loss', tMax, dt, with_purification=False)
        #lossArrValue = QNET.L2P(lossArr[0]) 
        #fidArr = QNET.getOptimalLossArray(Q, 'A', 'B', 'fid', tMax, dt, with_purification=False)
        #fidArrValue = QNET.L2P(fidArr[0])
        
        # Find the loss cost-type of the shortest path
        lossArrValue = nx.shortest_path_length(Q, Q.getNode('A'), Q.getNode('B'), weight='loss', method='dijkstra')
        
        # Find the fidelity cost-type of the shortest path        
        fidArrValue = nx.shortest_path_length(Q, Q.getNode('A'), Q.getNode('B'), weight='fid', method='dijkstra')  
        
        # Check if path exists        
        pathExists = pathExists + 1
    except:
        print("Loss cost type loop: No path exists")
        
        
    """
    # Faster algorithm to check if path exists
    if nx.has_path(Q, list(Q.nodes)[0], list(Q.nodes)[-1]):
        pathExists = pathExists + 1 
    """           
    return pathExists, lossArrValue, fidArrValue


    

    
























