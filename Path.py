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

        assert (isinstance(G, QNET.Qnet)), "path.__init__ requires reference to the graph containing the path"
        assert (array != None), "path.__init__ received an empty array"
        
        self.G = G
        self.node_array = []

        if all(isinstance(node, QNET.Qnode) for node in array):
            self.node_array = array

        elif all(isinstance(node, str) for node in array):
            for name in array:
                node = G.getNode(name)
                self.node_array.append(node)
        else:
            assert(False), "Path __init__ requires an array of strings or Qnodes"
            
        # Assert path is valid in G
        for i in range(len(self.node_array) - 1):
            if (self.node_array[i], self.node_array[i+1]) in G.edges():
                pass
            elif (self.node_array[i+1], self.node_array[i]) in G.edges():
                pass
            else:
                assert (False), f"Path {self.stringify()} does not exist in Qnet."

        # Potentially shorter way of doing it?
        #if all([(array[i], array[i + 1]) in G.edges() for i in range(len(array) - 1)
        #        or (array[i + 1], array[i]) in G.edges() for i in range(len(array) - 1)]):
        #    pass
            
    def __str__(self):
        return(self.stringify())
    
    def __repr__(self):
        return(self.stringify())

    def is_valid(self):
        """
        Checks to see if the given path is valid for entanglement distribution.
        :return: Boolean
        """
        has_ground = False
        for node in self.node_array:
            if isinstance(node, QNET.Ground) or isinstance(node, QNET.Satellite):
                has_ground = True
                break
        return has_ground

    def cost(self, costType):
        """
        Calculate the cost of the path for a given cost type
        :param str costType:
        :return: cost
        """

        # Convert cost to additive form
        assert(costType in ['p', 'e']), "Usage: costType in {'p', 'e'}"
        if costType == 'p':
            costType = 'd'
        elif costType == 'e':
            costType = 'log_e'
        else:
            assert(False), 'A weird exception has occurred'

        cost = 0
        pathLen = len(self.node_array)

        # Sum all edge costs of the path
        i = 0
        while (i < pathLen - 1):
            cur = self.node_array[i]
            nxt = self.node_array[i+1]
            edgeData = self.G.get_edge_data(cur, nxt)
            
            assert edgeData != None, "Path does not exist in graph"
            assert edgeData[costType] != None, f"costType \'{costType}\' does not exist between qnodes \'{cur.name}\' and \'{nxt.name}\'"

            cost += edgeData[costType]
            i += 1

        # Sum all node costs of the path
        for node in self.node_array:
            cost += node.costs[costType]

        # Convert costs back to linear form
        if costType == 'd':
            cost = QNET.fid_convert(cost, 'p')
        elif costType == 'log_e':
            cost = QNET.convert(cost, 'linear')
        else:
            assert(False), 'A weird exception has occurred.'

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
    
    def head(self):
        return self.node_array[0]
    
    def tail(self):
        return self.node_array[len(self.node_array) - 1]