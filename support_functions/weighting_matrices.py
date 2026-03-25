import numpy as np

def compute_weighting_matrices(NUM_STATES, NUM_INPUTS, number_atomic_agents, model, state_weighting_matrix, input_weighting_matrix):

    # Standard cost function

    if Q_cost == []:
        Q_cost = np.zeros((number_atomic_agents * NUM_STATES, number_atomic_agents * NUM_STATES))
        agent_idx = 0
        for i in range(0,number_atomic_agents):
            Q_cost[agent_idx, agent_idx] = 100
            Q_cost[agent_idx + 1, agent_idx + 1] = 10
            Q_cost[agent_idx + 2, agent_idx + 2] = 1
            agent_idx += NUM_STATES
    else:
        Q_cost = np.array(state_weighting_matrix)

    if R_cost == []:
        R_cost = np.zeros((number_atomic_agents * NUM_INPUTS, number_atomic_agents * NUM_INPUTS))
        if model == "linear":
            agent_idx = 0
            for i in range(0,number_atomic_agents):
                R_cost[agent_idx, agent_idx] = 1
                R_cost[agent_idx + 1, agent_idx + 1] = 1
                R_cost[agent_idx + 2, agent_idx + 2] = 1
                agent_idx += NUM_INPUTS
        elif model == "nonlinear":
            agent_idx = 0
            for i in range(0,number_atomic_agents):
                R_cost[agent_idx, agent_idx] = 1
                R_cost[agent_idx + 1, agent_idx + 1] = 1
                agent_idx += NUM_INPUTS
    else:
        R_cost = np.array(input_weighting_matrix)
    
    return Q_cost, R_cost
        