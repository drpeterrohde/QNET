#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 02:42:49 2020

@author: deepeshsingh
"""



import QNET
import numpy as np

def altLinGen(n, spacing, eVal = 1, pxVal = 0, pyVal = 0, pzVal = 0):
    '''
    Constructs a linear chain with end Qnodes A and B, and alternating Swapper and Ground nodes in the middle.

    Parameters
    ----------
    n : int
        Total number of nodes in the chain, including end nodes A and B.
    spacing : Array of float
        Distance between two consecutive nodes in [x,y,z] format.
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
        A linear chain of length n consisting of alternating Bell pair generator and swappers.  

    '''
    
    Q = QNET.Qnet()

    if n>0:    
        firstNode = QNET.Qnode(name = 'A', coords = spacing)
        Q.add_node(firstNode)
    
    previousNode = QNET.Qnode()
    currentNode = QNET.Qnode()
    
    ChannelList = []

    if n>2:    
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
                ChannelList.append({'edge': (previousNode.name, currentNode.name), 'e': eVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})
            
            previousNode = currentNode

    if n>1:     
        lastNode = QNET.Qnode(name = 'B', coords = np.multiply(n, spacing))
        Q.add_node(lastNode)
    
        ChannelList.append({'edge': (firstNode.name, list(Q.nodes)[1].name), 'e': eVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})
        ChannelList.append({'edge': (list(Q.nodes)[n-2].name, lastNode.name), 'e': eVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})
    
    Q.add_qchans_from(ChannelList)
     
    return Q


def altLinSatGen(n, spacing, eVal = 1, pxVal = 0, pyVal = 0, pzVal = 0, satCoord = [0,0,0], satVel = [0,0]):
    '''
    Constructs a linear chain with end Qnodes A and B, and alternating Swapper and Ground nodes in the middle.
    
    A satellite is connected to end nodes A and B, and all swapper nodes. 

    Parameters
    ----------
    n : int
        Total number of nodes in the chain, including end nodes A and B.
    spacing : Array of float
        Distance between two consecutive nodes in [x,y,z] format.
    eVal : float
        Efficiency of a single channel in the regular lattice. The default is 1.
    pxVal : float
        Probability of state not undergoing X-flip in the regular lattice. The default is 0.
    pyVal : float
        Probability of state not undergoing Y-flip in the regular lattice. The default is 0.
    pzVal : float
        Probability of state not undergoing Z-flip in the regular lattice. The default is 0.
    satCoord : Array of float
        Initial coordinates of the satellite node in [x,y,z] format. The default is [0,0,0].
    satVel : Array of float
        Initial velocity of the satellite node in [x,y] format. The default is [0,0].

    Returns
    -------
    Q : QNET Graph
        A linear chain of length n consisting of alternating Bell pair generator and swappers.
        End nodes A and B, and all swapper nodes are connected to a satellite. 

    '''   
    
    Q = QNET.Qnet()

    if n>0:    
        firstNode = QNET.Qnode(name = 'A', coords = spacing)
        Q.add_node(firstNode)
    
    previousNode = QNET.Qnode()
    currentNode = QNET.Qnode()
    
    ChannelList = []

    if n>2:    
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
                ChannelList.append({'edge': (previousNode.name, currentNode.name), 'e': eVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})
            
            previousNode = currentNode

    if n>1:     
        lastNode = QNET.Qnode(name = 'B', coords = np.multiply(n, spacing))
        Q.add_node(lastNode)
    
        ChannelList.append({'edge': (firstNode.name, list(Q.nodes)[1].name), 'e': eVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})
        ChannelList.append({'edge': (list(Q.nodes)[n-2].name, lastNode.name), 'e': eVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})

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
     
    return Q




    
