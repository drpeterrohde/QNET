#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 02:42:49 2020

@author: deepeshsingh
"""



import networkx as nx
import QNET
import numpy as np
import matplotlib.pyplot as plt


# Returns a linear chain with end Qnodes A and B, and alternating Swapper and Ground nodes in the middle
# Argument n (integer): Total number of nodes in the chain, including end nodes A and B
# Argument spacing (array): Distance between two consecutive nodes
# Argument loss (float): Loss between two consecutive nodes
def altLinGen(n, spacing, loss):
    assert(n>2)
    
    Q = QNET.Qnet()
    
    firstNode = QNET.Qnode(name = 'A', coords = spacing)
    Q.add_node(firstNode)
    
    previousNode = QNET.Qnode()
    currentNode = QNET.Qnode()
    
    ChannelList = []
    
    for i in range(n-2):
        GroundNode = QNET.Ground(name = ('G'+str(i+1)), coords = np.multiply(i+2, spacing))
        SwapNode = QNET.Swapper(name = ('T'+str(i+1)), coords = np.multiply(i+2, spacing))
        
        if n>3:
            if (i)%2==0:
                currentNode = SwapNode          
            else:
                currentNode = GroundNode    
        else:
            currentNode = GroundNode
            
        Q.add_node(currentNode)    

        if i>0:
            ChannelList.append({'edge': (previousNode.name, currentNode.name), 'loss': loss})
            
        previousNode = currentNode
     
    lastNode = QNET.Qnode(name = 'B', coords = np.multiply(n, spacing))
    Q.add_node(lastNode)
    
    ChannelList.append({'edge': (firstNode.name, list(Q.nodes)[1].name), 'loss': loss})
    ChannelList.append({'edge': (list(Q.nodes)[n-2].name, lastNode.name), 'loss': loss})
    Q.add_qchans_from(ChannelList)
    
    """
    for i in Q.nodes:
        print(i.name, i.coords)
    for i in Q.edges:
        print(i[0].name, i[1].name)
    """  
    return Q


# Returns a linear chain with end Qnodes A and B, and alternating Swapper and Ground nodes in the middle
# Adds a satellite in the Network. Satellite is connected to both end nodes (A and B) and all swappers in the linear chain
# Argument n (integer): Total number of nodes in the chain, including end nodes A and B
# Argument spacing (array): Distance between two consecutive nodes in the ground linear chain
# Argument loss (float): Loss between two consecutive nodes in the ground linear chain
# Argument satCoord (array): Initial coordinates of the Satellite Node
# Argument satCoord (array): Initial x and y components of the Satellite Node velocity 
def altLinSatGen(n, spacing, loss, satCoord, satVel):
    assert(n>2)
    
    Q = QNET.Qnet()
    
    firstNode = QNET.Qnode(name = 'A', coords = spacing)
    Q.add_node(firstNode)
    
    previousNode = QNET.Qnode()
    currentNode = QNET.Qnode()
    
    ChannelList = []
    
    for i in range(n-2):
        GroundNode = QNET.Ground(name = ('G'+str(i+1)), coords = np.multiply(i+2, spacing))
        SwapNode = QNET.Swapper(name = ('T'+str(i+1)), coords = np.multiply(i+2, spacing))
        
        if n>3:
            if (i)%2==0:
                currentNode = SwapNode          
            else:
                currentNode = GroundNode    
        else:
            currentNode = GroundNode
            
        Q.add_node(currentNode)    

        if i>0:
            ChannelList.append({'edge': (previousNode.name, currentNode.name), 'loss': loss})
            
        previousNode = currentNode
     
    lastNode = QNET.Qnode(name = 'B', coords = np.multiply(n, spacing))
    Q.add_node(lastNode)
    
    ChannelList.append({'edge': (firstNode.name, list(Q.nodes)[1].name), 'loss': loss})
    ChannelList.append({'edge': (list(Q.nodes)[n-2].name, lastNode.name), 'loss': loss})

    S = QNET.Satellite(name = 'S', coords = satCoord, velocity = satVel)
    Q.add_node(S)
    print(S.name)
    
    nodeList = Q.nodes()
    for node in nodeList:
        if type(node) != QNET.Ground and type(node) != QNET.Satellite:
            ChannelList.append({'edge': (node.name, S.name), 'loss': S.airCost(node)})            
            #ChannelList.append(node, S, loss = S.airCost(node))
            # G.add_edge(node, S2, loss = QNET.airCost(S2, node))
            
    Q.add_qchans_from(ChannelList)
    
    """
    for i in Q.nodes:
        print(i.name, i.coords)
    for i in Q.edges:
        print(i[0].name, i[1].name)
    """  
    return Q




    