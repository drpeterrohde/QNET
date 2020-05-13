#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 17:22:47 2020

@author: hudson
"""

import networkx as nx
import QNET
import numpy as np
import copy
import warnings

typeDict = {'Ground': QNET.Ground, 
     'Satellite': QNET.Satellite, 
     'Swapper': QNET.Swapper,
     'PBS': QNET.PBS,
     'CNOT': QNET.CNOT}

class Qnet(nx.Graph):
    
    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)
        
    def __str__(self):
        qnodes = ""
        for node in self.nodes():
            qnodes += (node.name)
            qnodes += ', '
            
        qchans = ""
        for chan in self.edges():
            edge_data = self.get_edge_data(chan[0], chan[1])
            qchans += str(chan[0].name + " <--> " + chan[1].name + " -- Costs: " + str(edge_data))
            qchans += "\n"
            
        return(f"Qnodes:\n{qnodes}\n\nQchans:\n{qchans}")
    
    ### QNET functions ###
    def add_qnode(self, qnode_type = None, **kwargs):
        """
        Initialize a qnode of some type and add it to the grah

        :param str qnode_type: qnode subclass
        :param kwargs: Keyword arguments needed to initialize the qnode

        :return: None
        """

        # Check that arguments exist
        assert len(kwargs) > 0

        # If type is specified, initialize qnode of that type
        if qnode_type != None:
            # Check if qnode_type is valid
            assert(qnode_type in typeDict), f"Unsupported qnode type: \'{qnode_type}\'"
            newNode = typeDict[qnode_type](**kwargs)

            # TODO: Add additional cost vector dict?
            self.add_node(newNode, **newNode.costs)

        # Else, initialize default qnode
        else:
            newNode = QNET.Qnode(**kwargs)
            self.add_node(newNode)
            
    
    # Convert array of tuples into Qnode objects and add to graph
    # First arguement is class. If class is unspecified, node will be regular qnode
    def add_qnodes_from(self, nbunch):
        """
        Initialize list of qnodes and adds them to a graph
        
        Parameters
        __________
        nbunch: array
            Array of dictionaries with qnode attributes as key-value pairs
            
        
        """
        for data in nbunch:
            self.add_qnode(**data)
            
    def add_qchan(self, edge = None, e = 1, p = 1, px = 0, py = 0, pz = 0, **kwargs):
        """
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
        
        u = self.getNode(edge[0])
        v = self.getNode(edge[1])

        cost_vector = QNET.make_cost_vector(p, e, px, py, pz, **kwargs)
        self.add_edge(u, v, **cost_vector)

            
    def add_qchans_from(self, cbunch):
        """
        Adds a list of channels connecting Qnodes

        Parameters
        ----------
        cbunch : array
            Array of dictionaries with channel attributes as key-value pairs

        Returns
        -------
        None.

        """
        
        for edge in cbunch:
            self.add_qchan(**edge)
        
    
    # Might be outmoded by for edge in G.edges() print edge
    def print_qchans(self):
        """
        Print every channel in the qnet graph

        Returns
        -------
        None.

        """
        for chan in self.edges():
            # get costs:
            edge_data = self.get_edge_data(chan[0], chan[1])
            print(chan[0].name + " <--> " + chan[1].name + " -- Costs: " + str(edge_data))
            
    
    # Given a nodeName and a graph, returns node
    def getNode(self, nodeName):
        """
        Returns a qnode object with a given name. Assumes uniqueness

        Parameters
        ----------
        nodeName : TYPE
            DESCRIPTION.

        Returns
        -------
        node : qnode
            qnode with matching name

        """
        for node in self.nodes():
            if node.name == nodeName:
                return node
        # else
        assert False, f"Node \"{nodeName}\" not found in graph."
    
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
                    
                    # Get new air cost
                    if isinstance(edge[0], QNET.Satellite):
                        newCost = edge[0].airCost(edge[1])
                    else:
                        newCost = edge[1].airCost(edge[0])
                    
                    # Update edge
                    self.add_edge(edge[0], edge[1], loss = newCost)

    def purify(self, sourceName, targetName):
        """

        Parameters
        ----------
        sourceName : str
            Name of source node
        targetName : str
            Name of destination node

        Returns
        -------
        int
            Purified cost of the network from source to target

        """
        
        def fidTransform(F1, F2):
            return (F1 * F2) / (F1 * F2 + (1 - F1) * (1 - F2) )

        # Get paths for Graph
        u = self.getNode(sourceName)
        v = self.getNode(targetName)
        generator = nx.all_simple_paths(self, u, v)

        # Get p values for each path
        p_arr = []
        for path in generator:
            new_path = QNET.Path(self, path)
            # check if path is valid
            if new_path.is_valid() == True:
                p = new_path.cost('p')
                p_arr.append(p)
            else:
                pass

        assert(len(p_arr) != 0), f"No path exists from {sourceName} to {targetName}"

        # Initialize purified fidelity as the max fidelity value
        pure_cost = max(p_arr)
        p_arr.remove(pure_cost)
        
        # Purify fidelities together
        while (len(p_arr) != 0):
            pmax = max(p_arr)
            if pmax > 0.5:
                pure_cost = fidTransform(pure_cost, pmax)
            elif pmax <= 0.5:
                break
            p_arr.remove(pmax)

        return pure_cost
    
    ### IN PROGRESS ###
    def low_purify(self, path1, path2, return_as = 'loss'):
        
        # If the paths are not QNET paths, make them
        if not isinstance(path1, QNET.Path):
            path1 = QNET.Path(G = self, array = path1)
        if not isinstance(path2, QNET.Path):
            path2 = QNET.Path(G = self, array = path2)
        
        # Check that both paths start and finish in the same place
        assert(path1.head() == path2.head()), "Paths do not start in the same place."
        assert(path1.tail() == path2.tail()), "Paths do not end in the same place."
        
        def fidTransform(F1, F2):
            return (F1 * F2) / (F1 * F2 + (1 - F1) * (1 - F2) )
        
        # Todo: Calc and return
        
        