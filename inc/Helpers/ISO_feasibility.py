import networkx as nx
import collections


def check_feasibility(node1, node2, G1, G2, G1_labels, G2_labels, mapping, reverse_mapping, T1, T1_out, T2, T2_out):
    # todo: add IND, SUB cases as well
    if G1_labels[node1] != G2_labels[node2]:
        return False

    if G1.number_of_edges(node1, node1) != G2.number_of_edges(node2, node2):
        return False

    if prune_ISO(G1, G2, G1_labels, G2_labels, node1, node2, mapping, reverse_mapping, T1, T1_out, T2, T2_out):
        return False
    # Check if every covered neighbor of u is mapped to every covered neighbor of v
    # Also check if there is the same number of edges between the candidates and their neighbors
    for neighbor in G1[node1]:
        if neighbor in mapping:
            if mapping[neighbor] not in G2[node2]:
                return False
            elif G1.number_of_edges(node1, neighbor) != G2.number_of_edges(node2, mapping[neighbor]):
                return False

    for neighbor in G2[node2]:
        if neighbor in reverse_mapping:
            if reverse_mapping[neighbor] not in G1[node1]:
                return False
            elif G1.number_of_edges(node1, reverse_mapping[neighbor]) != G2.number_of_edges(node2, neighbor):
                return False
    return True


def prune_ISO(G1, G2, G1_labels, G2_labels, u, v, mapping, reverse_mapping, T1, T1_out, T2, T2_out):
    u_neighbors_labels = {n1: G1_labels[n1] for n1 in G1[u]}
    u_labels_neighbors = collections.OrderedDict(sorted(nx.utils.groups(u_neighbors_labels).items()))

    v_neighbors_labels = {n2: G2_labels[n2] for n2 in G2[v]}
    v_labels_neighbors = collections.OrderedDict(sorted(nx.utils.groups(v_neighbors_labels).items()))
    # if the neighbors of u, do not have the same labels as those of v, NOT feasible.
    if set(u_labels_neighbors.keys()) != set(v_labels_neighbors.keys()):
        return True

    for labeled_nh1, labeled_nh2 in zip(u_labels_neighbors.values(), v_labels_neighbors.values()):
        if len(T1.intersection(labeled_nh1)) != len(T2.intersection(labeled_nh2)) or \
                len(T1_out.intersection(labeled_nh1)) != len(T2_out.intersection(labeled_nh2)):
            return True

    return False
