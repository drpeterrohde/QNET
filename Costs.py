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
import copy
import string


# Basic conversions
def to_log(x):
    return -np.log(x) + 0


def from_log(x):
    return np.exp(-x)


def to_add_f(x):
    return -np.log(np.abs(2 * x - 1)) + 0


def from_add_f(x):
    return (1 + np.exp(-1 * x)) / 2


def make_cost_vector(Q, **kwargs):
    """
    Creates a dictionary of costs for a node or edge.
    Efficiency and Fidelity are initalized, as are their additive costs and any other key word arguements specified
    by the user.

    :param float e: Proportion of photons that pass through the channel
    :param float p: Proportion of surviving photons that haven't changed state. Range: (0.5, 1)
    :param float kwargs: Other costs or qualifying attributes
    :return dictionary: Cost vector
    """
    # The default cost vector
    cost_vector = copy.copy(Q.cost_vector)
    # The valid ranges of each cost
    cost_ranges = Q.cost_ranges
    # The conversion methods from multiplicative cost to additive and vice versa
    conversions = Q.conversions

    # Update the cost vector with all valid costs found in kwargs
    for item in kwargs.items():
        key = item[0]
        if key in cost_vector:
            cost_vector.update([item])

    # Assert that costs are within the correct range:
    for item in cost_vector.items():
        name, value = item[0], item[1]
        cost_range = cost_ranges[name]
        cost_min, cost_max = cost_range[0], cost_range[1]
        assert (cost_min <= value <= cost_max), f"Out of range -- ({cost_min} <= {name} <= {cost_max}), " + \
                                                f"{name} == {value}"

    # Initialize additive costs
    additive_costs = {}
    for item in cost_vector.items():
        name, value = item[0], item[1]
        add_cost_func = conversions[name][0]
        additive_costs["add_" + name] = add_cost_func(value)
    cost_vector.update(additive_costs)

    return cost_vector


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

    conversions = Q.conversions
    assert cost_type in conversions, f"Invalid cost type. \"{cost_type}\" not in {str([key for key in conversions])}"
    # Change cost type to additive
    cost_type = "add_" + cost_type

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

    conversions = Q.conversions
    assert cost_type in conversions, f"Invalid cost type. \"{cost_type}\" not in {str([key for key in conversions])}"
    # Change cost type to additive
    cost_type = "add_" + cost_type

    # Calculate best cost in terms of additive cost
    weight = get_weight_function(cost_type)
    cost = nx.shortest_path_length(Q, source, target, weight)
    # Compensate shortest path cost with 1/2 head cost and 1/2 tail cost
    cost += source.costs[cost_type] / 2 + target.costs[cost_type] / 2

    # Convert multiplicative costs back to additive costs
    back_convert = conversions[cost_type.strip("_add")][1]
    cost = back_convert(cost)

    return cost
