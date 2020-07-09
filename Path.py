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

        node_array = []
        for node in array:
            node = G.getNode(node)
            assert node is not None
            node_array.append(node)

        self.G = G
        self.node_array = node_array
        self.head = node_array[0]
        self.tail = node_array[len(self.node_array) - 1]

        # Assert path is valid in G
        # Maybe we could just incorperate this into is_valid instead?
        if all([(node_array[i], node_array[i + 1]) in G.edges() \
                or (node_array[i + 1], node_array[i]) in G.edges() for i in range(len(node_array) - 1)]):
            pass
        else:
            assert False, f"Path {self.stringify()} does not exist in Qnet."

    def __str__(self):
        return self.stringify()

    def __repr__(self):
        return self.stringify()

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

    def cost(self, cost_type):
        """
        Calculate the cost of the path for a given costType.
        If calculating efficiency, does not take into account cost due to swapper node.

        Calculate the cost of the path for a given cost type
        :param str costType:
        :param str exclude: Node type to exclude from path length
        :return: cost
        """

        # Convert cost to additive form
        conversions = self.G.conversions
        assert cost_type in conversions, f"Invalid cost type. \"{cost_type}\" not in {str([key for key in conversions])}"
        cost_type = "add_" + cost_type

        cost = 0
        path_len = len(self.node_array)

        # Sum all edge costs of the path
        i = 0
        while i < path_len - 1:
            cur = self.node_array[i]
            nxt = self.node_array[i + 1]
            edge_data = self.G.get_edge_data(cur, nxt)

            assert edge_data is not None, "Path does not exist in graph"
            assert edge_data[cost_type] is not None, \
                f"costType \'{cost_type}\' does not exist between qnodes \'{cur.name}\' and \'{nxt.name}\'"

            cost += edge_data[cost_type]
            i += 1

        # Sum all node costs of the path
        for node in self.node_array:
            cost += node.costs[cost_type]

        # Convert multiplicative costs back to additive costs
        # Fixed a bug here... Maybe this might not work?
        cost_type = QNET.remove_prefix(cost_type, "add_")
        back_convert = conversions[cost_type][1]
        cost = back_convert(cost)

        return cost

    def cost_vector(self):
        cv = {}
        for cost in self.G.cost_vector.keys():
            if cost.startswith("add_") is False:
                val = self.cost(cost)
                cv[cost] = val
        return cv

    # TODO Test this
    def subgraph(self):
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

    def remove_edges(self):
        """
        Remove all edges in path from the graph G
        :return: None
        """
        path_len = len(self.node_array)
        i = 0
        while i < path_len - 1:
            cur = self.node_array[i]
            nxt = self.node_array[i + 1]
            self.G.remove_edge(cur, nxt)
            i += 1
