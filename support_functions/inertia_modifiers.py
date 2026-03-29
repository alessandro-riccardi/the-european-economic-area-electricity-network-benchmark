import numpy as np

def compute_inertia_modifiers(dispatchable_capacities, atomic_agents):

    number_atomic_agents = len(atomic_agents)
    
    global_inertia_modifiers = dispatchable_capacities/np.mean(dispatchable_capacities)
    inertia_modifiers = np.zeros(number_atomic_agents)


    for idx in range(number_atomic_agents):
        agent_idx = atomic_agents[idx]

        inertia_modifiers[idx] = global_inertia_modifiers[agent_idx]

    return inertia_modifiers