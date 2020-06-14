#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 18:59:10 2020

@author: deepeshsingh and Hudson Leone
"""
import networkx as nx
import QNET
import numpy as np
import Percolation as Pc
import copy
import statistics as stats

def iterations(Q, nTurns = 100, nSteps = 11, toCompute = "pathProbability"):
    '''
    Monte-Carlo iterations on a graph. 
    
    Calculates the probability of the existence of a path, efficiency of the shortest path, and fidelity of 
    the shortest path in a given graph for different percolation thresholds. 
    
    Parameters
    ----------
    Q : QNET Graph
        Input graph.
    nTurns : int
        Number of Monte-Carlo iterations. The default is 100.
    nSteps : int
        Number of data points to be plotted. The default is 11.
    toCompute : String
        Describes the type of data point for which the computation is performed:
        ["pathProbability", "efficiency", "fidelity", "purFidelity"].
        The default is "pathProbability".
    progress_bar : Boolean
        Indicates whether or not user wants to print a progress bar as the operation proceeds

    Returns
    -------
    avg : Array of float
        Average value of toCompute i.e. "pathProbability", "efficiency", or "fidelity".
    var : Array of float
        Variance value of toCompute i.e. "pathProbability","efficiency", or "fidelity".

    '''

    def try_append_cost(G, cost_array, to_compute):
        """
        This subfunction attempts to calculate the a cost for a percolated lattice
        and append it to a cost_array. If successful, the value is appended to cost_array
        and the function returns true. Else it returns false. (I.E. A path didn't exist)

        :param G: Percolated lattice graph
        :param list cost_array: Array where costs are stored
        :param string to_compute: Any of ["efficiency", "fidelity", "purFidelity]
        :return: Boolean
        """
        assert to_compute in ["efficiency", "fidelity", "purFidelity"]

        if to_compute == "efficiency":
            cost_type = 'e'
        elif to_compute == "fidelity":
            cost_type = 'p'

        if to_compute == "purFidelity":
            try:
                cost_value = G.purify("A", "B")
                cost_array.append(cost_value)
                return True
            except:
                return False

        else:
            try:
                cost_value = QNET.shortest_path_length(G, list(G.nodes)[0], list(G.nodes)[-1], cost_type)
                cost_array.append(cost_value)
                return True
            except:
                return False

    # Begin iterations():
    assert(nTurns > 1)

    # Copy of square lattice
    B = copy.deepcopy(Q)

    # Range of percolation densities to calculate for
    DefectProb = np.linspace(0, 1, nSteps)

    # Arrays for mean and standard deviation at different percolation values
    avg = []
    var = []
       
    for probThresh in DefectProb:

        if toCompute == "pathProbability":
            # Monte-carlo Implementation to calculate probability of path existing
            num_valid_paths = 0

            for i in range(nTurns):
                G = Pc.defectedGraph(B, probThresh)
                if nx.has_path(G, list(G.nodes)[0], list(G.nodes)[-1]):
                    num_valid_paths = num_valid_paths + 1

            mean = num_valid_paths / nTurns
            avg.append(mean)
            # Note: If X = Path exist then X in [0, 1]
            # Hence E(X^2) = E(X)
            # And Var(X) = 1/(n-1) (E(X) - E(X)^2)
            var.append(np.sqrt( 1/(nTurns-1) * (mean - mean**2) ))
        
        elif toCompute in ["efficiency", "fidelity", "purFidelity"]:

            # List of costs for a specific percolation density. These will be used to calculate mean and std.
            cost_array = []

            for i in range(nTurns):
                G = Pc.defectedGraph(B, probThresh)
                try_append_cost(G, cost_array, toCompute)

            # If no valid paths, e = 0 with no uncertainty.
            if len(cost_array) == 0:
                avg.append(0)
                var.append(0)

            # If one valid path, statistics.stdev() cannot be calculated. Opt to keep trying until we get another value.
            elif len(cost_array) == 1:
                got = False
                while got is False:
                    G = Pc.defectedGraph(B, probThresh)
                    got = try_append_cost(G, cost_array, toCompute)

                mean = stats.mean(cost_array)
                avg.append(mean)
                var.append(stats.variance(cost_array, mean))

            else:
                mean = stats.mean(cost_array)
                avg.append(mean)
                var.append(stats.variance(cost_array, mean))

        else:
            print("Enter valid data type to be computed: pathProbability, efficiency, fidelity or purFidelity")


    return avg, var