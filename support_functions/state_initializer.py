import numpy as np

def compute_initial_state_linear(atomic_agents, INITIAL_DISPATCHABLE_POWER):
    
    NUMBER_ATOMIC_AGENTS = len(atomic_agents)
    NUM_STATES = 5
    INITIAL_DISPATCHABLE_POWER = INITIAL_DISPATCHABLE_POWER.reshape(-1)

    
    # This function should compute the initial state of the system based on the initial conditions of the network.
    # The specific implementation will depend on the structure of the state vector and the initial conditions provided.
    # For example, if the state vector includes voltage angles, frequencies, and power injections for each atomic agent, 
    # you would need to extract this information from the initial conditions and populate the state vector accordingly.
    
    # Placeholder implementation (to be replaced with actual logic):
    initial_state = np.zeros(NUM_STATES * NUMBER_ATOMIC_AGENTS)

    for idx in range(NUMBER_ATOMIC_AGENTS):
        agent_idx = atomic_agents[idx]

        initial_state[idx*(NUM_STATES) + 4] = INITIAL_DISPATCHABLE_POWER[agent_idx]
    
    return initial_state