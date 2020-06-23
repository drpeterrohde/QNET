"""
Costs.py contains all of the relevant software for instantiating cost vectors, converting between various cost types
and calculating optimal path costs

Definitions:
    p:
        Fidelity.
    e:
        Efficiency. The proportion of photons that make it through a channel
    log_e:
        -log(e)
    d:
        -log(abs(1 - 2p))
"""
import networkx as nx
import QNET
import numpy as np

def make_cost_vector(e=1, p=1, **kwargs):
    """
    Creates a dictionary of costs for a node or edge.
    Efficiency and Fidelity are initalized, as are their additive costs and any other key word arguements specified
    by the user.

    :param float e: Proportion of photons that pass through the channel
    :param float p: Proportion of surviving photons that haven't changed state. Range: (0.5, 1)
    :param float pz: Probability of z-flip (Dephasing)
    :param float kwargs: Other costs or qualifying attributes
    :return dictionary: Cost vector
    """
    cost_vector = {'e': e, 'p': p}
    cost_vector.update(kwargs)

    # Assert that costs are within the correct range:
    assert (0 <= e <= 1), "Out of range"
    assert (0 <= p <= 1), "Out of range"

    # Convention in Qnet: p > 0.5
    if p < 0.5:
        p = 1 - p

    # Initialize additive costs
    cost_vector['log_e'] = log_convert(e, 'log')
    cost_vector['d'] = fid_convert(p, 'd')

    # Initialize other attributes
    for arg in kwargs:
        cost_vector[arg] = kwargs[arg]

    return cost_vector


def log_convert(x, typ):
    """
    Convert a value to a linear or logarithmic regime.
    Handles infinities and other exceptions

    :param float x: Value to convert
    :param str typ: Type to convert to. Usage: {'log', 'linear}
    :return float: Converted value
    """
    valid_types = ['log', 'linear']
    assert (typ in valid_types), "Invalid type, please choose one from {\'log\', \'linear\'}"

    if typ == 'log':
        assert (0 <= x <= 1)
        return -1 * np.log(x) + 0
    else:
        assert (0 <= x)
        return (np.exp(-x))


def fid_convert(x, typ):
    """
    Convert the fidelity 'p' into its additive form (d = -log(2p - 1)) or vice versa.
    :param float x: Value to convert
    :param str typ: Type to convert to. Usage: {'p', 'd'}
    :return float: Converted value
    """
    valid_types = ['p', 'd']
    assert (typ in valid_types), "Invalid type, please choose one from {\'p\', \'d\'}"

    if typ == 'd':
        return -np.log(np.abs(2 * x - 1)) + 0
    else:
        return (1 + np.exp(-1 * x)) / 2


def best_path(Q, source, target, cost_type):
    """
    Given a source node, target node, and a cost type, this function returns the path that optimises this cost.
    :param Q: Qnet graph
    :param source: Source node
    :param target: Target node
    :param cost_type: Any valid cost type from the cost vector
    :return: string
    """
    def get_weight_function(costType):
        """
        Given a costType, returns a corresponding weight_function
        for use in nx.shortest_path_length

        :param string costType: cost type in ['e', 'p']
        :return: weight function
        """
        def weight(u, v, d):
            node_u_wt = u.costs[costType]
            node_v_wt = v.costs[costType]
            # Attempts to get edge weight, returns 1 if not found
            edge_wt = d.get(costType, 1)
            return node_u_wt / 2 + node_v_wt / 2 + edge_wt
            # Note that shortest path cost will need to be compensated with 1/2 head and 1/2 tail cost
        return weight

    source = Q.getNode(source)
    target = Q.getNode(target)

    # Convert multiplicative costs to additive costs
    convert_dict = {'e':'log_e', 'p':'d'}
    if cost_type in convert_dict:
        cost_type = convert_dict[cost_type]

    weight = get_weight_function(cost_type)
    path = nx.dijkstra_path(Q, source, target, weight)
    # Convert array of nodes to Path class
    path = QNET.Path(Q, path)
    return path


def best_path_cost(Q, source, target, cost_type):
    """
    Get the lowest path cost in a Qnet for a given costType.
    Considers edge weights and node weights
    # TODO Considers only valid paths.

    :param Q: Qnet Graph
    :param Union[str, Qnode] source: Source node
    :param Union[str, Qnode] target: Target node
    :param str costType: Any of {'e', 'p', 'de', 'dp'}
    :return: float length of shortest path in units of costType
    """

    def get_weight_function(costType):
        """
        Given a costType, returns a corresponding weight_function
        for use in nx.shortest_path_length

        :param string costType: cost type in ['e', 'p']
        :return: weight function
        """
        def weight(u, v, d):
            node_u_wt = u.costs[costType]
            node_v_wt = v.costs[costType]
            # Attempts to get edge weight, returns 1 if not found
            edge_wt = d.get(costType, 1)
            return node_u_wt / 2 + node_v_wt / 2 + edge_wt
            # Note that shortest path cost will need to be compensated with 1/2 head and 1/2 tail cost
        return weight

    source = Q.getNode(source)
    target = Q.getNode(target)

    # Convert multiplicative costs to additive costs
    convert_dict = {'e': 'log_e', 'p': 'd'}
    if cost_type in convert_dict:
        cost_type = convert_dict[cost_type]

    # Calculate shortest_cost
    weight = get_weight_function(cost_type)
    cost = nx.shortest_path_length(Q, source, target, weight)
    # Compensate shortest path cost with 1/2 head cost and 1/2 tail cost
    cost += source.costs[cost_type]/2 + target.costs[cost_type]/2

    # Convert multiplicative costs back to additive costs
    if cost_type == 'log_e':
        cost = log_convert(cost, 'linear')
    elif cost_type == 'd':
        cost = fid_convert(cost, 'p')

    return cost