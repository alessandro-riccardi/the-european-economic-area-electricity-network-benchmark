import numpy as np

def compute_reference_trajectory_linear_standard(atomic_agents, SIMULATION_HORIZON, PREDICTION_HORIZON, EEA_ENB):

    NUMBER_ATOMIC_AGENTS = len(atomic_agents)
    NUM_STATES = EEA_ENB.NUM_STATES

    Reference_Signal = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+PREDICTION_HORIZON))

    return Reference_Signal


def compute_reference_trajectory(model, reference_signal_generator, atomic_agents, SIMULATION_HORIZON, PREDICTION_HORIZON, EEA_ENB):
    if model == 'linear' and reference_signal_generator == 'Standard':
        return compute_reference_trajectory_linear_standard(atomic_agents, SIMULATION_HORIZON, PREDICTION_HORIZON, EEA_ENB)
    else:
        # Here add the reference trajectory computation for the other combinations of model and reference signal generator when the function is implemented
        raise ValueError(f"Model '{model}' or reference signal generator '{reference_signal_generator}' not recognized. Please choose 'linear' and 'Standard'.")
        
    