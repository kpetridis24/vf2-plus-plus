def find_candidates(G1, G2, G1_labels, G2_labels, u, mapping, reverse_mapping):
    covered_neighbors = {nbr for nbr in G1[u] if nbr in mapping}
    if len(covered_neighbors) == 0:
        return {node for node in G2.nodes() if
                node not in reverse_mapping and G2.degree[node] == G1.degree[u] and G2_labels[node] == G1_labels[
                    u] and len([nbr2 for nbr2 in G2[node] if nbr2 in reverse_mapping]) == 0}

    G2_uncovered_neighborhoods = []
    for neighbor1 in covered_neighbors:
        current_neighborhood = set()
        for neighbor2 in G2[mapping[neighbor1]]:
            current_neighborhood.add(neighbor2)
        G2_uncovered_neighborhoods.append(current_neighborhood)

    common_nodes = set.intersection(*G2_uncovered_neighborhoods)
    candidates = {node for node in common_nodes if G1_labels[u] == G2_labels[node] and G1.degree[u] == G2.degree[node]}

    return candidates
