# %% Mark: Import libraries
import numpy as np
import pandas as pd
import sys
from support_functions.options import parse_arguments
from support_functions.weighting_matrices import compute_weighting_matrices
from support_functions.network_bounds import compute_network_bounds
from data_preprocessing import data_process_sampling

# ADD ARGPARSER
# Remember matrices Q and R in the argparser
# Add a sa parameter the list of electrical areas to simulate




# %% Settings

# if __name__ == "__main__":

sys.argv = ["main.py", 
            "--electrical_areas", "[17, 2, 6, 10]",
            "--control_time_step", "0.5", 
            "--number_hours", "24",
            "--model", "linear",
            "--control_strategy", "centralized",
            "--partitioning_strategy", "none",
            "--simulation_horizon", "100",
            "--prediction_horizon", "10",
            "--state_weighting_matrix", "[]",
            "--input_weighting_matrix", "[]",
            "--consensus_treshold", "1e-6",
            "--preprocess_data", "",
            "--plot_data", "True",
            "--store_data", "True"
            ]

# %% Mark: Import data

dispatchable_capacities = np.loadtxt('electricity_data/Capacities_List.csv', delimiter=',')

args = parse_arguments()

# %% MARK: Network configuration
electrical_areas = args.electrical_areas
electrical_areas.sort() # Sort the list of electrical areas to ensure consistent ordering

atomic_agents = []
for area_idx in range(len(electrical_areas)):
    atomic_agents.append(electrical_areas[area_idx] - 1) # Subtract 1 to convert from 1-based indexing to 0-based indexing

number_atomic_agents = len(atomic_agents)

model = args.model

if model == "linear":
    NUM_STATES = 5
    NUM_INPUTS = 3
elif model == "nonlinear":
    NUM_STATES = 5
    NUM_INPUTS = 2

# Simulation configuration
PREPROCESS_DATA = args.preprocess_data
PLOT_DATA = args.plot_data
STORE_DATA = args.store_data

control_time_step = args.control_time_step
number_hours = args.number_hours

Q_cost, R_cost = compute_weighting_matrices(NUM_STATES, NUM_INPUTS, number_atomic_agents, model, args.state_weighting_matrix, args.input_weighting_matrix)

upper_bounds_states, lower_bounds_states, upper_bounds_inputs, lower_bounds_inputs = compute_network_bounds(atomic_agents, number_atomic_agents, NUM_STATES, NUM_INPUTS, dispatchable_capacities, control_time_step)

# %% Mark: Construct dataset

if PREPROCESS_DATA:
    data_process_sampling.preprocess_data(control_time_step, number_hours, PLOT_DATA, STORE_DATA)






# %% Mark: Contruct network topology



# %% Mark: Define network dynamics

# INITIALIZE NETWORK

# RUN MPC

# PLOT AND STORE RESULTS