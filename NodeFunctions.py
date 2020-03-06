#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 11:32:15 2020

@author: hudson
"""
import QNET
import numpy as np
import scipy.integrate
from pvlib import atmosphere

# Convert array of tuples into Qnode objects and add to graph
# First arguement is class. If class is unspecified, node will be regular qnode
def add_qnodes_from(G, nbunch):
    
    # qnodes = []
    # dictionary of nodeTypes to classes:
    typeDict = {'Ground': QNET.Ground, 
     'Satellite': QNET.Satellite, 
     'Swapper': QNET.Swapper,
     'PBS': QNET.PBS,
     'CNOT': QNET.CNOT}
    
    for node in nbunch:
        assert node != None
        if node[0] in typeDict:
            # put the rest of the arguements into tuple
            args = []
            i = 1
            while i < len(node):
                args.append(node[i])
                i += 1
            # Initialise new class
            newNode = typeDict[node[0]](*args)
            
            assert(type(newNode) != None)
            
            # qnodes.append(newNode)
            G.add_node(newNode)
            
        else:
            # Check to see if object is likely qnode. Raise error if not
            if len(node) != 2 or len(node[1]) != 3:
                assert False, f"Unsupported Qnode type: \"{node[0]}\""
            newNode = QNET.Qnode(*node)
            assert(type(newNode) != None)
            
            # qnodes.append(newNode)
            G.add_node(newNode)
    
    #return qnodes
        

# Given a nodeName and a graph, returns node
def getNode(G, nodeName):
    for node in G.nodes():
        if node.name == nodeName:
            return node
    # else
    assert False, f"Node \"{nodeName}\" not found in graph."

# def addNodes(nodeList)
    

# Distance between nodes
def distance(u, v):
        
    ux = u.coords[0]
    uy = u.coords[1]
    uz = u.coords[2]
        
    vx = v.coords[0]
    vy = v.coords[1]
    vz = v.coords[2]
        
    return np.sqrt((ux - vx)**2 + (uy - vy)**2 + (uz - vz)**2)


# Cost function of satellite to node through air, assuming nodes are on ground level
def airCost(u, v):
    
    # Identify which of (u, v) is the satellite:
    if type(u) == QNET.Satellite:
        s = u
        n = v
    elif type(v) == QNET.Satellite:
        s = v
        n = u
        s = v
        n = u
    else:
        print("Warning! No satellite class given! Returning None")
        return(None)

    alt = s.coords[2]
        
    # Calculate ground distance from source to target:
    dist = distance(s, n)
        
    # Calculate azimuthal angle 
    theta = np.arcsin(alt / dist)
        
        
    """
    Line integral for effective density
        
      / L'
     |     rho(L * sin(theta)) dL
    /   0
    """
        
    def rho(L, theta):
        # From altitude, calculate pressure
        # Assume T = 288.15K and 0% humidity
        P = atmosphere.alt2pres(L * np.sin(theta))
        T = 288.15
        R = 287.058 # Specific gas constant of air
        return P / (R * T)
        
    # Perform numerical integreation to get effective density (?)
    result = scipy.integrate.quad(rho, 0, dist, args = (theta))[0]
    
    return result * 0.1

# Update Satellite positions
def updateSatPos(G, dt):
    for node in G.nodes:
        if type(node) == QNET.Satellite:
            # Update satellite position:
            node.posUpdate(dt)
            
def updateSatChannels(G, dt):
    for node in G.nodes:
        if type(node) == QNET.Satellite:
            # Get neighboring channels:           
            edges = G.edges(node)
            # Update channels:
            for edge in edges:
                newCost = QNET.airCost(edge[0], edge[1])
                # Update edge
                G.add_edge(edge[0], edge[1], loss = newCost)

# Update all time dependent elements
def update(G, dt):
    updateSatPos(G, dt)
    updateSatChannels(G, dt)
    
# Distribute swapping costs over the network
def swap(G, costType):
    for node in G.nodes:
        if type(node) == QNET.Swapper:
            # Fetch neighboring channels:
            edges = G.edges(node)
            for edge in edges:
                oldCost = G[edge[0]][edge[1]][costType]
                newCost = oldCost + (1 / node.prob) / len(edges)
                G.add_edge(edge[0], edge[1], costType = newCost)
            