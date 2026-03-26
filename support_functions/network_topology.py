import numpy as np
import os


def compute_network_topology(LIST_ATOMIC_AGENTS):

    NUMBER_ATOMIC_AGENTS = len(LIST_ATOMIC_AGENTS)

    # Load full adjacency matrix
    WEIGHTED_ADJACENCY_MATRIX_RAW = np.loadtxt(os.path.normpath(os.path.join('topological_data', 'Adj_W.csv')), delimiter=',')

    # Construct the weighted adjacency matrix
    Weighted_Adjacency_Matrix = np.zeros((NUMBER_ATOMIC_AGENTS,NUMBER_ATOMIC_AGENTS))
    for i in range(0,NUMBER_ATOMIC_AGENTS):
        Agent_i_idx = LIST_ATOMIC_AGENTS[i]
        for j in range(0,NUMBER_ATOMIC_AGENTS):
            Agent_j_idx = LIST_ATOMIC_AGENTS[j] 
            Weighted_Adjacency_Matrix[i,j] = WEIGHTED_ADJACENCY_MATRIX_RAW[Agent_i_idx,Agent_j_idx]

    return Weighted_Adjacency_Matrix