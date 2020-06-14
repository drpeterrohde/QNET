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
        if len(self.nodes()) == 0:
            qnodes += "None\n"
        else:
            for node in self.nodes():
                qnodes += "Name: " + "\"" + node.name + "\"" + '\n'\
                    + str(type(node)) + '\n'\
                    + "Coordinates: " + str(node.coords) + '\n'\
                    + "Costs: " + str(node.costs) + '\n'\

                if isinstance(node, QNET.Satellite):
                    qnodes += "Cartesian == " + str(node.cartesian) + '\n'
                    if node.cartesian == True:
                        qnodes += "Velocity == " + str(node.velocity) + '\n'

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

        return (f"\n-- Qnodes --\n\n{qnodes}-- Qchans --\n{qchans}")

    ### QNET functions ###
    def add_qnode(self, qnode_type=None, **kwargs):
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
            assert (qnode_type in typeDict), f"Unsupported qnode type: \'{qnode_type}\'"
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

    def add_qchan(self, edge=None, e=1, p=1, px=0, py=0, pz=0, **kwargs):
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

        u = self.getNode(edge[0])
        v = self.getNode(edge[1])

        # If either of the nodes are satellites, get air costs
        if isinstance(u, QNET.Satellite):
            e, p = u.airCost(v)
        elif isinstance(v, QNET.Satellite):
            e, p = v.airCost(u)

        cost_vector = QNET.make_cost_vector(e, p, px, py, pz, **kwargs)
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
                    self.add_qchan(edge = [s.name, n.name], e=new_e, p=new_p)

    def purify(self, sourceName, targetName, method = "path_disjoint"):
        """
        This function performs a multi-path entanglement purification between a source and target node using all
        available paths.

        :param str sourceName: Name of source node
        :param targetName: Name of target node
        :param string, optional (default = "edge_disjoint"), method: The method used to do the purification.
        Supported options: "edge_disjoint", "node_disjoint", "total_disjoint", "greedy".
            edge_disjoint: No intersecting edges
            node_disjoint: No intersecting nodes
            total_disjoint: No intersecting edges or nodes
            greedy:  
        Other inputs produce a ValueError
        :return: float

        """

        def fidTransform(F1, F2):
            return (F1 * F2) / (F1 * F2 + (1 - F1) * (1 - F2))

        # Get paths for Graph
        u = self.getNode(sourceName)
        v = self.getNode(targetName)

        # TODO: Test this fix
        generator = nx.node_disjoint_paths(self, u, v)

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

        assert (len(p_arr) != 0), f"No path exists from {sourceName} to {targetName}"

        # Initialize purified fidelity as the max fidelity value
        pure_cost = max(p_arr)
        p_arr.remove(pure_cost)

        # Purify fidelities together
        # TODO: Depreciate this code
        while (len(p_arr) != 0):
            pmax = max(p_arr)
            if pmax > 0.5:
                pure_cost = fidTransform(pure_cost, pmax)
            elif pmax <= 0.5:
                break
            p_arr.remove(pmax)

        return pure_cost

    # TODO Test this:
    def bi_purify(self, path1, path2, costType):
        """
        Returns the purified path cost of two paths in the graph
        :param Union[str, Path] path1:
        :param Union[str, Path] path2:
        :param str costType: Any of {'p', 'dp'}
        :return float: Purified cost
        """
        assert (costType in ['p', 'dp']), "Usage: CostType in (\'p\', \'dp\')."

        # If the paths are not QNET paths, make them
        if not isinstance(path1, QNET.Path):
            path1 = QNET.Path(G=self, array=path1)
        if not isinstance(path2, QNET.Path):
            path2 = QNET.Path(G=self, array=path2)

        # Check that both paths start and finish in the same place
        assert (path1.head() == path2.head()), "Paths do not start at the same node."
        assert (path1.tail() == path2.tail()), "Paths do not end at the same node."

        # Assert that no nodes except for head and tail are coincident in (path1, path2)
        weakest_link = min(len(path1.node_array), len(path2.node_array))
        for i in range(weakest_link):
            if (i == 0 or i == weakest_link - 1):
                pass
            else:
                if path1.node_array[i] == path2.node_array[i]:
                    assert False, f"Paths have coincident nodes in body. Cannot purify."

        def fidTransform(F1, F2):
            return (F1 * F2) / (F1 * F2 + (1 - F1) * (1 - F2))

        p1 = path1.cost('p')
        p2 = path2.cost('p')

        if p1 >= 0.5 and p2 >= 0.5:
            pur_cost = fidTransform(p1, p2)
        else:
            pur_cost = max(p1, p2)

        if costType == 'dp':
            pur_cost = QNET.convert(pur_cost, 'log')

        return pur_cost
