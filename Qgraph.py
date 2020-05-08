#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 17:22:47 2020

@author: hudson
"""

import networkx as nx
import QNET
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
    def add_qnode(self, **kwargs):
        """
        From a tuple, initializes a qnode and adds it to a graph
        
        TODO: How to initialize a docstring for **kwargs?

        """
        
        # If type is something, intialise with that.
        
        # Check that arguements exist
        assert len(kwargs) > 0
        # Pop node type from kwarg dict and initialise a node of that type
        qnode_type = kwargs.pop('qnode_type', None)
        if qnode_type != None:
            # Check if qnode_type is valid
            assert(qnode_type in typeDict), f"Unsupported qnode type: \'{qnode_type}\'"
            newNode = typeDict[qnode_type](**kwargs)
            self.add_node(newNode)
        # If type not specified, initialise default node type
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
        # Currently works for an array of dictionaries
        
        # Basically want all or most of the data options that networkX can handle.
        
        for data in nbunch:
            self.add_qnode(**data)
            
    def add_qchan(self, **kwargs):
        """
        Parameters
        ----------
        **kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        assert len(kwargs) > 0
        edge = kwargs.pop('edge', None)
        assert (edge != None), "\'edge\' is a required key word arguement for qchan"
        assert (len(edge) == 2), "'\edge\' must be an array-like object of length 2"
        
        u = self.getNode(edge[0])
        v = self.getNode(edge[1])
        
        self.add_edge(u, v, **kwargs)
            
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
                    
    
    def unwrap(self, sourceName, targetName):
        """
        Generates a dictionary of all simple paths from source to dest with losses as values

        Parameters
        ----------
        sourceName : str
            Name of source node
        targetName : str
            Name of destination node

        Returns
        -------
        pathDict : dict
            Dictionary with paths as keys and losses as values

        """
        # Create graph copy:
        C = copy.deepcopy(self)
        
        source = C.getNode(sourceName)
        target = C.getNode(targetName)
    
        # initialize dictionary
        pathDict = {}
        
        while(nx.has_path(C, source, target)):
            
            # TODO
            # Might be a generator, not a path
            shortest = QNET.Path(C, nx.shortest_path(C, source, target, weight = 'loss'))
            
            # Get path cost: (possibly buggy)
            shortCost = shortest.cost(costType = 'loss')
            
            # Add path and cost to pathDict
            pathDict[shortest] = shortCost
            
            # Require that paths are disjoint
            # Hence remove all nodes from shortest except source and target
            for node in shortest.node_array:
                if node != source and node != target:
                    C.remove_node(node)
                    
            assert(C.has_node(source))
            assert(C.has_node(target))
                
        return pathDict
    
       
    def purify(self, sourceName, targetName, return_as = 'loss'):
        """
        Calculate the purified cost from source to target
        
        Parameters
        ----------
        sourceName : str
            Name of source node
        targetName : str
            Name of destination node
        return_as : str, optional
            Specify the units to recieve the calculation in. 
            Choose between {'loss', 'fid'}. The default is 'loss'.

        Returns
        -------
        int
            Purified cost of the network from source to target

        """
        
        def fidTransform(F1, F2):
            return (F1 * F2) / (F1 * F2 + (1 - F1) * (1 - F2) )
        
        # Array of path fidelities
        fidArr = []
        
        # Unwrap graph into dictionary of QNET paths to losses
        pathDict = self.unwrap(sourceName, targetName)
        
        # Extract fidelities
        for key in pathDict:
            loss = pathDict[key]
            # Convert from loss to fid
            fid = QNET.L2P(loss)
            fidArr.append(fid)
        
        assert(len(fidArr) != 0), "Error in Qnet.Purify: No path exists from SourceName to targetName"
        
        # Is there at least one fid s.t. fid > 0.5? If not, return max fidelity
        if all(i < 0.5 for i in fidArr):
            if return_as == 'loss':
                return(QNET.P2L(max(fidArr)))
            elif return_as == 'fid':
                return(max(fidArr))
            else:
                assert(False), "Invalid return type in purify.\n Usage: return_as = {'loss', 'fid}"
                
        
        # Initialize purified fidelity as the max fidelity value
        purFid = max(fidArr)
        fidArr.remove(purFid)
        
        # Purify fidelities together
        while (len(fidArr) != 0):
            maxfid = max(fidArr)
            if maxfid > 0.5:
                purFid = fidTransform(purFid, maxfid)
            fidArr.remove(maxfid)
        
        if return_as == 'loss':
            return(QNET.P2L(purFid))
        elif return_as == 'fid':
            return purFid
        else:
            assert(False), "Invalid return type in purify.\n Usage: return_as = {'loss', 'fid}"
            
    
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
        
        