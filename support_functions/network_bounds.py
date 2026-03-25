import numpy as np

def compute_network_bounds(atomic_agents, number_atomic_agents, NUMBER_STATES, NUMBER_INPUTS, dispatchable_capacities, control_time_step):

    steps_per_hour = 3600 / control_time_step

    # Compute the bounds for the state and input variables for each atomic agent in the network

    upper_bounds_states = np.zeros((NUMBER_STATES, number_atomic_agents))
    lower_bounds_states = np.zeros((NUMBER_STATES, number_atomic_agents))
    upper_bounds_inputs = np.zeros((NUMBER_INPUTS, number_atomic_agents))
    lower_bounds_inputs = np.zeros((NUMBER_INPUTS, number_atomic_agents))

    for idx in range(number_atomic_agents):
        agent_idx = atomic_agents[idx]
        # Define the bounds for the state variables for this atomic agent
        upper_bounds_states[:, idx] =  np.array([3.5,
                                                 0.05,
                                                 dispatchable_capacities[agent_idx]/1000,
                                                 0,
                                                 dispatchable_capacities[agent_idx]/1000])
        
        lower_bounds_states[:, idx] =  np.array([-3.5,
                                                 -0.05,
                                                 0,
                                                 0,
                                                 0])
        
        upper_bounds_inputs[:, idx] = np.array([dispatchable_capacities[agent_idx]/1000/steps_per_hour,
                                                dispatchable_capacities[agent_idx]/1000/steps_per_hour,
                                                dispatchable_capacities[agent_idx]/1000/steps_per_hour])
        
        lower_bounds_inputs[:, idx] = np.array([-dispatchable_capacities[agent_idx]/1000/steps_per_hour,
                                                0,
                                                0])
        
    return upper_bounds_states, lower_bounds_states, upper_bounds_inputs, lower_bounds_inputs
