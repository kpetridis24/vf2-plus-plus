import collections

import networkx as nx
from inc.Helpers.candidates import find_candidates
from inc.Helpers.feasibility import feasibility
from inc.Helpers.node_ordering import matching_order
from inc.Helpers.state import (
    restore_state,
    update_state,
)


def VF2pp(G1, G2, G1_labels, G2_labels):
    try:
        m = next(isomorphic_VF2pp(G1, G2, G1_labels, G2_labels))
        return m
    except StopIteration:
        return None


def isomorphic_VF2pp(G1, G2, G1_labels, G2_labels):
    """Implementation of the VF2++ algorithm.

    Parameters
    ----------
    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism.

    G1_labels,G2_labels: dict
        The label of every node in G1 and G2 respectively.

    Returns
    -------
    True and the node mapping, if the two graphs are isomorphic. False and None otherwise.
    """
    if not G1 and not G2:
        return False
    if not precheck(G1, G2, G1_labels, G2_labels):
        return False

    graph_params, state_params, node_order, stack = initialize_VF2pp(
        G1, G2, G1_labels, G2_labels
    )
    matching_node = 1
    mapping = state_params.mapping

    while stack:
        current_node, candidate_nodes = stack[-1]

        try:
            candidate = next(candidate_nodes)
            if feasibility(current_node, candidate, graph_params, state_params):
                if len(mapping) == G1.number_of_nodes() - 1:
                    mapping.update({current_node: candidate})
                    yield state_params.mapping

                update_state(
                    current_node,
                    candidate,
                    matching_node,
                    node_order,
                    stack,
                    graph_params,
                    state_params,
                )
                matching_node += 1

        except StopIteration:
            stack.pop()
            matching_node -= 1
            if stack:
                restore_state(stack, graph_params, state_params)


def precheck(G1, G2, G1_labels, G2_labels):
    """Checks if all the pre-requisites are satisfied before calling the isomorphism solver.

    Notes
    -----
    Before trying to create the mapping between the nodes of the two graphs, we must check if:
    1. The two graphs have equal number of nodes
    2. The degree sequences in the two graphs are identical
    3. The two graphs have the same label distribution. For example, if G1 has orange nodes but G2 doesn't, there's no
    point in proceeding to create a mapping.

    Parameters
    ----------
    G1,G2: NetworkX Graph or MultiGraph instances.
        The two graphs to check for isomorphism or monomorphism.

    G1_labels,G2_labels: dict
        The label of every node in G1 and G2 respectively.
    """
    if G1.order() != G2.order():
        return False
    if sorted(d for n, d in G1.degree()) != sorted(d for n, d in G2.degree()):
        return False

    nodes_per_label1 = {
        label: len(nodes) for label, nodes in nx.utils.groups(G1_labels).items()
    }
    nodes_per_label2 = {
        label: len(nodes) for label, nodes in nx.utils.groups(G2_labels).items()
    }

    if nodes_per_label1 != nodes_per_label2:
        return False

    return True


def initialize_VF2pp(G1, G2, G1_labels, G2_labels):
    mapping, reverse_mapping = dict(), dict()
    T1, T2 = set(), set()
    T1_out, T2_out = set(G1.nodes()), set(G2.nodes())

    GraphParameters = collections.namedtuple(
        "GraphParameters", ["G1", "G2", "G1_labels", "G2_labels"]
    )
    StateParameters = collections.namedtuple(
        "StateParameters",
        ["mapping", "reverse_mapping", "T1", "T1_out", "T2", "T2_out"],
    )

    graph_params = GraphParameters(G1, G2, G1_labels, G2_labels)
    state_params = StateParameters(mapping, reverse_mapping, T1, T1_out, T2, T2_out)

    node_order = matching_order(G1, G2, G1_labels, G2_labels)

    starting_node = node_order[0]
    candidates = find_candidates(starting_node, graph_params, state_params)
    stack = [(starting_node, iter(candidates))]

    return graph_params, state_params, node_order, stack


def prepare_next(stack, node_order, state_params):
    entering_node, _ = stack.pop()
    node_order.appendleft(entering_node)
    popped_node1, _ = stack[-1]
    popped_node2 = state_params.mapping[popped_node1]
    state_params.mapping.pop(popped_node1)
    state_params.reverse_mapping.pop(popped_node2)
