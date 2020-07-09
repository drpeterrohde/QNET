#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 17:22:47 2020
@author: hudson
"""

import networkx as nx
import QNET
from typing import Callable

typeDict = {'Ground': QNET.Ground,
            'Satellite': QNET.Satellite,
            'Swapper': QNET.Swapper}


class Qnet(nx.Graph):
    def __init__(self, cost_vector=None, cost_ranges=None, conversions=None, incoming_graph_data=None, **attr):
        """
        Initialization method
        :param cost_vector:
        cost_vector is a dictionary containing costs and values. All objects in the Qnet graph are initialized with this
        object. All costs are assumed to be multiplicative (like probability) unless the cost has the prefix "add_", in
        which case it will be additive. The keys in cost_vector are the valid costs for the Qnet graph, and the values
        are the default magnitudes of these costs.

        If cost_vector is none, then self.cost_vector = {'e':1, 'p':1, 'add_e':0, 'add_p':0}.
        For details on Qnet cost vectors and the default costs, please consult the documentation in Costs.py

        :type cost_vector: Dict[str, int], optional

        :param conversions:
        A dictionary that maps Qnet costs to a pair of conversion functions to and from the additive cost respectively.
        The keys of these dictionaries are the valid costs for the Qnet graph, and the values are lists of conversion
        functions that accept one float inputs and return a single float.
        conversions = {'cost': [func to convert to additive, func to convert to multiplicative]}

        :type conversions: Dict[str, [Callable, Callable]]

        :param incoming_graph_data: Additional graph data.
        See NetworkX documentation: https://networkx.github.io/documentation/stable/reference/classes/graph.html#methods

        :param attr: Additional attributes.
        See NetworkX documentation: https://networkx.github.io/documentation/stable/reference/classes/graph.html#methods
        """
        if cost_vector is None and conversions is None:
            cost_vector = {'e': 1, 'f': 1}
            cost_ranges = {'e': (0, 1), 'f': (0.5, 1)}
            conversions = {'e': [QNET.to_log, QNET.from_log], 'f': [QNET.to_add_f, QNET.from_add_f]}
        else:
            assert set(cost_vector.keys()) == set(cost_ranges.keys()), \
                "Keys in \"cost_vector\" do not match keys in \"cost_ranges\""
            assert set(cost_vector.keys()) == set(conversions.keys()), \
                "Keys in \"cost_vector\" do not match keys in \"conversions\""
            for rng in cost_ranges.values():
                assert(len(rng) == 2),\
                    "Usage: cost_ranges = {cost: (min_val, max_val)}"
            for functions in conversions.values():
                assert(len(functions) == 2),\
                    "Usage: conversions = {'cost': [convert_to_additive, convert_to_multiplicative]}"

        self.cost_vector = cost_vector
        self.cost_ranges = cost_ranges
        self.conversions = conversions
        super().__init__(incoming_graph_data, **attr)

    def __str__(self):
        qnodes = ""
        if len(self.nodes()) == 0:
            qnodes += "None\n"
        else:
            for node in self.nodes():
                qnodes += "Name: " + "\"" + node.name + "\"" + '\n' \
                          + str(type(node)) + '\n' \
                          + "Coordinates: " + str(node.coords) + '\n' \
                          + "Costs: " + str(node.costs) + '\n'
                if isinstance(node, QNET.Satellite):
                    qnodes += "Cartesian == " + str(node.cartesian) + '\n'
                    if node.cartesian == True:
                        qnodes += "Velocity == " + str(node.velocity) + '\n'
                if isinstance(node, QNET.Swapper):
                    qnodes += "Swap probability == " + str(node.swap_prob) + '\n'

                qnodes += "\n"

        qchans = ""
        if len(self.edges()) == 0:
            qchans += "None\n"
        else:
            for chan in self.edges():
                edge_data = self.get_edge_data(chan[0], chan[1])
                qchans += str(chan[0].name + " <--> " + chan[1].name + '\n' +
                              "Costs: " + str(edge_data))
                qchans += "\n"

        return (f"-- Default cost vector --\n{self.cost_vector}\n-- Qnodes --\n{qnodes}-- Qchans --\n{qchans}")

    def add_qnode(self, qnode_type=None, **kwargs):
        """
        Initialize a qnode of some type and add it to the graph
        :param str qnode_type: qnode subclass
        :param kwargs: Keyword arguments needed to initialize the qnode
        :return: None
        """
        # if qnode_type is None, initialize as the default type.
        if qnode_type is None:
            new_node = QNET.Qnode(self, **kwargs)
        else:
            # Check if type is valid
            assert (qnode_type in typeDict), f"Unsupported qnode type: \'{qnode_type}\'"
            new_node = typeDict[qnode_type](self, **kwargs)

        # Check if node already exists in graph. If no, add new_node. If yes, update old node
        old_node = self.getNode(new_node.name)
        if old_node is None:
            self.add_node(new_node)
        else:
            old_node.update(self, **kwargs)

    def add_qnodes_from(self, nbunch):
        """
        Add qnodes from a dictionary.
        :param nbunch: Dictionary of nodes
        :return: None
        """
        for data in nbunch:
            self.add_qnode(**data)

    def remove_qnode(self, qnode):
        qnode = self.getNode(qnode)
        if qnode is None:
            return
        self.remove_node(qnode)

    def remove_qnodes_from(self, nbunch):
        for data in nbunch:
            self.remove_qnode(data)

    def add_qchan(self, edge=None, **kwargs):
        """
        Add a Qchan to the graph. If either of the node types are Satellites, the airCosts
        will be automatically calculated from current positions and added to the cost array.

        :param list edge: Array-like object of two qnodes to be connected
        :param float e: Proportion of photons that pass through the channel
        :param float p: Proportion of surviving photons that haven't changed state
        :param float px: Probability of x-flip (Bitflip)
        :param float py: Probability of y-flip
        :param float pz: Probability of z-flip (Dephasing)
        :param float kwargs: Other costs or qualifying attributes
        :return: None
        """

        # Assert edge is valid
        assert (edge != None), "\'edge\' must be an array-like object of two qnodes"
        assert (len(edge) == 2), "\'edge\' must be an array-like object of two qnodes"

        u = self.getNode(str(edge[0]))
        v = self.getNode(str(edge[1]))

        if u is None:
            u = QNET.Ground(self, name=str(edge[0]))
            self.add_node(u)
        if v is None:
            v = QNET.Ground(self, name=str(edge[1]))
            self.add_node(v)

        # If either of the nodes are satellites, get air costs
        if isinstance(u, QNET.Satellite):
            e, f = u.airCost(v)
            kwargs.update({'e': e, 'f': f})
        elif isinstance(v, QNET.Satellite):
            e, f = v.airCost(u)
            kwargs.update({'e': e, 'f': f})

        cost_vector = QNET.make_cost_vector(self, **kwargs)
        self.add_edge(u, v, **cost_vector)

    def add_qchans_from(self, cbunch):
        """
        Adds a list of channels connecting Qnodes
        """
        for edge in cbunch:
            self.add_qchan(**edge)

    def getNode(self, node_name):
        """
        This function returns a node of a given name. If no such node exists, returns None.
        :param node_name: Name of node
        :return: Node
        """
        if isinstance(node_name, QNET.Qnode):
            for node in self.nodes():
                if node.name == node_name.name:
                    return node
        for node in self.nodes():
            if node.name == node_name:
                return node
        return None

    def update(self, dt):
        """
        Updates all time dependent elements in the Qnet
        Parameters
        ----------
        dt : int
            Size of time increment
        Returns
        -------
        None.
        """
        assert (dt is not None)

        # Update satellite positions
        for node in self.nodes:
            if isinstance(node, QNET.Satellite):
                # Update satellite position:
                node.posUpdate(dt)

        # Update satellite channels
        for node in self.nodes:
            if isinstance(node, QNET.Satellite):
                # Get neighboring channels:           
                edges = self.edges(node)
                # Update channels:
                for edge in edges:
                    if isinstance(edge[0], QNET.Satellite):
                        s = edge[0]
                        n = edge[1]
                    else:
                        n = edge[0]
                        s = edge[1]

                    # newCost = [e, p]
                    newCost = s.airCost(n)

                    # Unpack newCost
                    new_e = newCost[0]
                    new_p = newCost[1]

                    # Update edge
                    self.remove_edge(s, n)
                    self.add_qchan(edge=[s.name, n.name], e=new_e, p=new_p)
