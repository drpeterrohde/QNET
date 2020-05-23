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

def RegLat(x, y, xspacing, yspacing = [0,0,0], eVal = 1, pVal = 1, pxVal = 0, pyVal = 0, pzVal = 0):
    '''
    Constructs a 2D Regular Lattice with end Qnodes A and B, and alternating Swapper and Ground nodes in the middle.
    

    Parameters
    ----------
    x : int
        Number of columns in the regular lattice.
    y : int
        Number of rows in the regular lattice.
    xspacing : 3x1 Array of float 
        Distance between two consecutive columns in 2D regular lattice in [x,0,0] format. 
    yspacing : 3x1 Array of float
        Distance between two consecutive rows in 2D regular lattice in [0,y,0] format. The default is [0,0,0].
    eVal : float
        Efficiency of a single channel in the regular lattice. The default is 1.
    pxVal : float
        Probability of state not undergoing X-flip in the regular lattice. The default is 0.
    pyVal : float
        Probability of state not undergoing Y-flip in the regular lattice. The default is 0.
    pzVal : float
        Probability of state not undergoing Z-flip in the regular lattice. The default is 0.

    Returns
    -------
    Q : QNET Graph
        A y*x 2D regular lattice.

    '''
        
    assert(x>0)
    assert(y>0)
    
    if yspacing==[0,0,0]:
        yspacing[1] = xspacing[0] 

    
    Q = QNET.Qnet()
    
    firstNode = QNET.Qnode(name = 'A', coords = [0,0,0])
    lastNode = QNET.Qnode(name = 'B', coords = np.add(np.multiply(x-1, xspacing), np.multiply(y-1, yspacing)))
    
    previousNode = QNET.Qnode()
    currentNode = QNET.Qnode()
    
    ChannelList = []
    
    # Constructing the nodes in the Regular Lattice
    for i in range(x):
        for j in range(y):

            GroundNode = QNET.Ground(name = ('G('+str(i+1)+','+str(j+1)+')'), coords = np.add(np.multiply(i, xspacing), np.multiply(j, yspacing)))
            SwapNode = QNET.Swapper(name = ('T('+str(i+1)+','+str(j+1)+')'), coords = np.add(np.multiply(i, xspacing), np.multiply(j, yspacing)))
            
            # Swap nodes at odd positions and Ground nodes at even positions in a Regular Lattice
            if x>=1 and y>=1:
                if (i+j)%2==0:
                    currentNode = GroundNode          
                else:
                    currentNode = SwapNode  
            
            # Linear chain of length 3 exception
            if (x==3 and y==1) or (x==1 and y==3):
                currentNode = GroundNode
                  
            # 2*2 2D lattice exception    
            if x==2 and y==2:
                currentNode = GroundNode
            
            # Initialising the first node as A
            if i==0 and j==0:
                currentNode = firstNode
             
            # Initialising the last node as B  
            if i==(x-1) and j==(y-1):
                currentNode = lastNode
             
            Q.add_node(currentNode)    
            
            previousNode = currentNode
              
         
    # Constructing the vertical edges in the Regular Lattice    
    for i in range(x):
        previousNode = list(Q.nodes)[i*y]
        for j in range(y-1):
            currentNode = list(Q.nodes)[j+1+(i*y)]
            ChannelList.append({'edge': (previousNode.name, currentNode.name), 'e': eVal, 'p': pVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})
            previousNode = currentNode
            
    # Constructing the horizontal edges in the Regular Lattice    
    for j in range(y):
        previousNode = list(Q.nodes)[j]
        for i in range(x-1):
            currentNode = list(Q.nodes)[j+(i+1)*y]
            ChannelList.append({'edge': (previousNode.name, currentNode.name), 'e': eVal, 'p': pVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})
            previousNode = currentNode
             
            
    Q.add_qchans_from(ChannelList)
    #Q.print_qchans()
     
    return Q




