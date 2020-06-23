#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 17:22:47 2020
@author: hudson
"""

import networkx as nx
import QNET

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

    def add_qnode(self, qnode_type=None, **kwargs):
        """
        Initialize a qnode of some type and add it to the graph
        :param str qnode_type: qnode subclass
        :param kwargs: Keyword arguments needed to initialize the qnode
        :return: None
        """

        # if qnode_type is None, initialize as the default type.
        if qnode_type is None:
            new_node = QNET.Qnode(**kwargs)
            old_node = self.getNode(new_node.name)
            if old_node is None:
                self.add_node(new_node)
            else:
                old_node.update(kwargs)
        else:
            # Check if type is valid
            assert (qnode_type in typeDict), f"Unsupported qnode type: \'{qnode_type}\'"
            new_node = typeDict[qnode_type](**kwargs)
            old_node = self.getNode(new_node.name)
            if old_node is None:
                self.add_node(new_node)
            else:
                self.update_qnode(old_node, **kwargs)

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
        assert qnode is not None
        self.remove_node(qnode)

    def remove_qnodes_from(self, nbunch):
        for data in nbunch:
            self.remove_qnode(data)

    def add_qchan(self, edge=None, e=1, p=1, **kwargs):
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
            u = QNET.Ground(name=str(edge[0]))
            self.add_node(u)
        if v is None:
            v = QNET.Ground(name=str(edge[1]))
            self.add_node(v)

        # If either of the nodes are satellites, get air costs
        if isinstance(u, QNET.Satellite):
            e, p = u.airCost(v)
        elif isinstance(v, QNET.Satellite):
            e, p = v.airCost(u)

        cost_vector = QNET.make_cost_vector(e, p, **kwargs)
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

    def getNode(self, node_name):
        """
        This function returns a node of a given name. If no such node exists, returns None.
        :param node_name: Name of node
        :return: Node
        """
        if isinstance(node_name, QNET.Qnode):
            return node_name
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
                    self.add_qchan(edge = [s.name, n.name], e=new_e, p=new_p)

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
