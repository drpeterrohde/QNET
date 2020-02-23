#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 11:32:16 2020
This is a module that converts a QNET network to a NetworkX graph
@author: Hudson
"""

import QNET
import networkx as nx

def q2x(Q):
    X = nx.Graph()
    
    # Initialise nodes
    for node in Q.nodes:
        qNode2x(node, X)
        
    # Initialise edges
    for channel in Q.channels:
        
        # Call in channel attributes
        chName = channel.name
        nodes = [channel.source, channel.dest]
        costs = channel.cost.costs
        
        # Check if nodes already exist in networkx graph
        i = 0
        while i < 2:
            doesNodeExist = [False, False]
            for node in X.nodes:
                if node == nodes[i].name:
                    doesNodeExist[i] = True
            i += 1
        
        # If nodes do not exist, create them add them to the network.
        i = 0
        while i < 2:
            if doesNodeExist[i] == False:
                name = nodes[i].name
                newNode = QNET.Node(name)
                qNode2x(newNode, X)
            i += 1
           
        # Create edges
        # The name is also the node, so just create edges with name
        X.add_edge(nodes[0].name, 
                   nodes[1].name, 
                   name = chName, 
                   nodes = nodes, 
                   **costs)

        # Create a dicctionary from attributes
    
    return X


# Takes a QNET node and networkX graph
# Turns the node into a networkX node and adds it to graph
def qNode2x(node, X):
    # Call in node attributes
    name = node.name
    coords = node.coords
    costs = node.cost.costs
        
    # Identify nodeType
    if isinstance(node, QNET.Satellite):
        nodeType = 'Satellite'
    else:
        nodeType = 'Ground'
        
    # Create a dictionary from attributes
    newDict = {'coords':coords, 'costs':costs, 'type':nodeType}
        
    # Create networkX node
    X.add_node(name, attr_dict = newDict)
