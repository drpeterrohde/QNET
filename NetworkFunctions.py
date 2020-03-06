#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 14:25:26 2020

@author: hudson
"""

import networkx as nx
import QNET
import copy
import numpy as np

# TODO: Decide on naming convention
# Should I use 'prob' or 'fid'?

def prob2loss(fid):
    return -1 * np.log(fid)

def loss2prob(cost):
    return np.exp(-cost)

# Given a path and a costType, returns the cost to traverse the path
def pathCost(G, path, costType):
    cost = 0
    pathLen = len(path)
    i = 0
    while (i < pathLen - 1):
        edgeData = G.get_edge_data(path[i], path[i + 1])
        cost += edgeData[costType]
        i += 1
    return cost


def unwrap(G, sourceName, targetName, costType, threshold = None):
    
    # Create copy of G:
    CG = copy.deepcopy(G)
    
    # get nodes from sourceName, targetName:
    
    # TODO Raise error if sourceName or targetName not in G!
    source = QNET.getNode(CG, sourceName)
    target = QNET.getNode(CG, targetName)

    # initialize dictionary
    pathDict = {}
    
    while(nx.has_path(CG, source, target)):
        
        # Find shortest path and write to tuple
        shortest = tuple(nx.shortest_path(CG, source, target, weight = costType))
        
        # get path cost: (possibly buggy)
        shortCost = pathCost(CG, shortest, costType)
        
        # Check path cost against threshold
        if threshold == None:
            pass
        elif shortCost > threshold:
            break
        
        # add path and cost to dictionary
        # keys must be an immutable data type (string, number, tuple)
        pathDict[shortest] = shortCost
        
        # remove path from graph:
        for node in shortest:
            if node != source and node != target:
                CG.remove_node(node)
            assert(CG.has_node(source))
            assert(CG.has_node(target))
            
    return pathDict


def purify(G, sourceName, targetName, costType, threshold = None):
    
    # Unwrap graph
    pathDict = unwrap(G, sourceName, targetName, costType, threshold)
    
    # Unpack pathDict into array of fidelities
    pathCosts = []
    
    for key in pathDict:
        val = pathDict[key]
        # Convert val from loss to probability:
        val = loss2prob(val)
        # debug
        print(val)
        pathCosts.append(val)
    
    # Initialize purified fidelity
    purFid = min(pathCosts)
    pathCosts.remove(purFid)
    
    # Combine costs according to fidelity function
    while(len(pathCosts) != 0):
        z = min(pathCosts)
        pathCosts.remove(z)
        purFid = fidTransform( purFid, z )
        
    # convert purFid into loss
    purFid = prob2loss(purFid)
    
    return purFid
        
        
def fidTransform(F1, F2):
    return (F1 * F2) / (F1 * F2 + (1 - F1) * (1 - F2) )