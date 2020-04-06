#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 12:00:05 2020

@author: hudson
"""

import networkx as nx
import QNET
import numpy as np

class Path:
    
    def __init__(self, G, array):
        
        assert (G != None), "path.__init__ requires reference to the graph containing path"
        assert(array != None), "path.__init__ recieved an empty array"
        
        self.G = G
        # TODO: name_array is redundant now
        self.name_array = None
        self.node_array = None
        
        # Check if array has strings or nodes, allocate accordingly
        if (isinstance(array[0], str)):
            self.name_array = array
            
        elif (type(array[0] == QNET.Qnode())):
            self.node_array = array
        
        # Check that allocation has been made. Raise exeption if not
        assert (self.name_array != None or
                self.node_array != None), "path.__init__ requires an array of nodes or node names for initialization"
        
        # If name_array is empty, use node_array to fill it up
        if self.name_array != None:
            node_array = []
            for name in self.name_array:
                node = G.getNode(name)
                node_array.append(node)
            self.node_array = node_array
        
        # If node_array is empty, use name_array to fill it up
        elif self.node_array != None:
            name_array = []
            for node in self.node_array:
                name = node.name
                name_array.append(name)
            self.name_array = name_array
            
        ## TODO: Assert path is valid ##
            
    def __str__(self):
        return(str(self.stringify()))
    
    def cost(self, costType):
        """
        Calculate the cost of the path for a given cost type

        Parameters
        ----------
        costType : str
            Units of the cost
            Choose between {'loss', 'fid'}. The default is 'loss'.

        Returns
        -------
        int

        """
        
        # UNIT CONVERSIONS
        def P2L(P):
            return -1 * np.log(P)

        # Convert loss to success probability
        def L2P(L):
            return np.exp(-L) 
        
        # Convert loss to fidelity
        def L2F(L):
            return np.exp(-L)
        
        cost = 0
        pathLen = len(self.node_array)
        i = 0
        while (i < pathLen - 1):
            cur = self.node_array[i]
            nxt = self.node_array[i+1]
            edgeData = self.G.get_edge_data(cur, nxt)
            
            assert edgeData != None, "Path does not exist in graph"
            assert edgeData[costType] != None, f"costType \'{costType}\' does not exist between qnodes \'{cur.name}\' and \'{nxt.name}\'"
            
            cost += edgeData[costType]
            
            # Add additional costs due to node type
            if (type(cur) == type(QNET.Swapper())):
                cost += cur.loss
            
            i += 1
            
        # Convert cost to specified costType
        if costType == 'fid':
            return L2F(cost)
        else:
            return cost
    
    # TODO Test this
    def subgraph(self):
        """
        Returns
        -------
        Qnet()
            A Qnet subgraph of the given path

        """
        return self.G.subgraph(self.array)
    
    # TODO: Test
    def stringify(self):
        """

        Returns
        -------
        pString : str
            Stringified version of the path

        """
        # Given a path, returns a string of the path
        pString = ""
        i = 0
        while i < len(self.node_array):
            pString = pString + str(self.node_array[i].name)
            i += 1
            if i < len(self.node_array):
                pString = pString + "-"
        return pString