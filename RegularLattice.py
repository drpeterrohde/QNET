#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 02:52:07 2020

@author: deepeshsingh
"""


import networkx as nx
import QNET
import numpy as np
import matplotlib.pyplot as plt


# Returns a linear chain with end Qnodes A and B, and alternating Swapper and Ground nodes in the middle
# Argument x (integer): Total number of nodes in the chain in x-direction, including end nodes A and B
# Argument y (integer): Total number of nodes in the chain in y-direction, including end nodes A and B
# Argument spacing (array): Distance between two consecutive nodes
# Argument loss (float): Loss between two consecutive nodes
def RegLat(x, y, xspacing, yspacing, loss):
    assert(x>1)
    assert(y>1)
    
    Q = QNET.Qnet()
    
    firstNode = QNET.Qnode(name = 'A', coords = [0,0,0])
    lastNode = QNET.Qnode(name = 'B', coords = np.add(np.multiply(x-1, xspacing), np.multiply(y-1, yspacing)))
    #Q.add_node(firstNode)
    
    previousNode = QNET.Qnode()
    currentNode = QNET.Qnode()
    
    ChannelList = []
    
    # Constructing the nodes in the Regular Lattice
    for i in range(x):
        for j in range(y):

            GroundNode = QNET.Ground(name = ('G('+str(i+1)+','+str(j+1)+')'), coords = np.add(np.multiply(i, xspacing), np.multiply(j, yspacing)))
            SwapNode = QNET.Swapper(name = ('T('+str(i+1)+','+str(j+1)+')'), coords = np.add(np.multiply(i, xspacing), np.multiply(j, yspacing)))
            
            if x>2 and y>2:
                if (i+j)%2==0:
                    currentNode = GroundNode          
                else:
                    currentNode = SwapNode    
            else:
                currentNode = GroundNode
                
            if i==0 and j==0:
                currentNode = firstNode
                
            if i==(x-1) and j==(y-1):
                currentNode = lastNode
             
            Q.add_node(currentNode)    
            
            previousNode = currentNode
              
         
    # Constructing the vertical edges in the Regular Lattice    
    for i in range(x):
        previousNode = list(Q.nodes)[i*y]
        for j in range(y-1):
            currentNode = list(Q.nodes)[j+1+(i*y)]
            ChannelList.append({'edge': (previousNode.name, currentNode.name), 'loss': loss})
            previousNode = currentNode
            
    # Constructing the horizontal edges in the Regular Lattice    
    for j in range(y):
        previousNode = list(Q.nodes)[j]
        for i in range(x-1):
            currentNode = list(Q.nodes)[j+(i+1)*y]
            ChannelList.append({'edge': (previousNode.name, currentNode.name), 'loss': loss})
            previousNode = currentNode
             
            
    Q.add_qchans_from(ChannelList)
    #Q.print_qchans()
     
    return Q




