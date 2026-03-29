# %% MARK: Import libraries
import numpy as np
import pandas as pd
import sys
from support_functions.options import parse_arguments
from support_functions.weighting_matrices import compute_weighting_matrices
from support_functions.network_bounds import compute_network_bounds
from data_preprocessing.data_process_sampling import preprocess_electrical_data
from support_functions.data_loader import import_electricity_data
from support_functions.network_topology import compute_network_topology
from topological_data.Network_Topology_Map import compute_topological_data
from support_functions.inertia_modifiers import compute_inertia_modifiers
from mpc_core.network_dynamics import network_dynamics_constructor
from support_functions.state_initializer import compute_initial_state_linear
from partitioning.partitioning_caller import network_partitioning
from partitioning.control_agents import compute_control_agents_matrices, compute_control_agents_matrices
from mpc_core.optimization_matrices import compute_optimization_matrices
from mpc_core.reference_generator import compute_reference_trajectory
from mpc_core.simulator import control_simulation

# ADD ARGPARSER
# Remember matrices Q and R in the argparser
# Add a sa parameter the list of electrical areas to simulate


# %% Settings 

# if __name__ == "__main__":

sys.argv = ["main.py", 
            # "--electrical_areas", "[17, 2, 6, 10]", # Uncomment this line to simulate a subset of the network, 
            "--control_time_step", "2.5", 
            "--number_hours", "24",
            "--model", "linear",
            "--control_strategy", "Centralized_MPC",
            "--partitioning_strategy", "centralized",
            "--simulation_horizon", "1440", 
            "--prediction_horizon", "10",
            "--reference_signal_generator", "Standard",
            "--state_weighting_matrix", "[]",
            "--input_weighting_matrix", "[]",
            "--consensus_treshold", "1e-6",
            "--preprocess_data", "",
            "--plot_data", "True",
            "--store_data", "True"
            ]


# %% MARK: Argument Parser

args = parse_arguments()


# Network configuration
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
simulation_horizon = args.simulation_horizon
prediction_horizon = args.prediction_horizon
partitioning_strategy = args.partitioning_strategy
reference_signal_generator = args.reference_signal_generator

# %% MARK: Data Preprocessing

# Only required to generate data the first time, or when the control time step changes
if PREPROCESS_DATA:
    compute_topological_data(PLOT_DATA, STORE_DATA)
    preprocess_electrical_data(control_time_step, number_hours, PLOT_DATA, STORE_DATA)


# %% MARK: Contruct network topology
Weighted_Adjacency_Matrix = compute_network_topology(atomic_agents)


# %% MARK: Import electricity data data

MEASURED_LOAD, MEASURED_RENEWABLE, MEASURED_LOAD_INCREMENTS, MEASURED_RENEWABLE_INCREMENTS, FORECAST_LOAD_INCREMENTS, FORECAST_RENEWABLE_INCREMENTS, INITIAL_DISPATCHABLE_POWER, dispatchable_capacities = import_electricity_data(atomic_agents, simulation_horizon, prediction_horizon)

# %% MARK: Plot Input Data


# %% MARK: Simulation parameters

# here add model
Q_cost, R_cost = compute_weighting_matrices(NUM_STATES, NUM_INPUTS, number_atomic_agents, model, args.state_weighting_matrix, args.input_weighting_matrix)

# here add model
upper_bounds_states, lower_bounds_states, upper_bounds_inputs, lower_bounds_inputs = compute_network_bounds(atomic_agents, number_atomic_agents, NUM_STATES, NUM_INPUTS, dispatchable_capacities, control_time_step)

inertia_modifiers = compute_inertia_modifiers(dispatchable_capacities, atomic_agents)


# %% MARK: Initialize Network Dynamics

EEA_ENB = network_dynamics_constructor(model, atomic_agents, Weighted_Adjacency_Matrix, control_time_step, inertia_modifiers, compute_initial_state_linear, INITIAL_DISPATCHABLE_POWER)

# %% MARK: Network Partitioning

# here add model
Control_Agents, Augmented_Control_Agents = network_partitioning(atomic_agents, partitioning_strategy, Weighted_Adjacency_Matrix)

# %% MARK: Augmented control agents dynamics

Control_Agents_Matrices = compute_control_agents_matrices(model, atomic_agents, Control_Agents, Augmented_Control_Agents, EEA_ENB, Q_cost, R_cost)


# %% MARK: Compute Optimization Matrices

Control_Agents_Optimization_Matrices = compute_optimization_matrices(model, Control_Agents, Augmented_Control_Agents, Control_Agents_Matrices, prediction_horizon, EEA_ENB)

# %% MARK: Compute Reference Trajectory

Reference_Signal = compute_reference_trajectory(model, reference_signal_generator, atomic_agents, simulation_horizon, prediction_horizon, EEA_ENB)


# %% MARK: Simulation Dictionary

simulation_data = {
    "model": model,
    "EEA_ENB": EEA_ENB,
    "control_strategy": args.control_strategy,
    "partitioning_strategy": args.partitioning_strategy,
    "electrical_areas": electrical_areas,
    "control_time_step": control_time_step,
    "number_hours": number_hours,
    "simulation_horizon": simulation_horizon,
    "prediction_horizon": prediction_horizon,
    "atomic_agents": atomic_agents,
    "number_atomic_agents": number_atomic_agents,
    "NUM_STATES": NUM_STATES,
    "NUM_INPUTS": NUM_INPUTS,
    "MEASURED_LOAD": MEASURED_LOAD,
    "MEASURED_RENEWABLE": MEASURED_RENEWABLE,
    "MEASURED_LOAD_INCREMENTS": MEASURED_LOAD_INCREMENTS,
    "MEASURED_RENEWABLE_INCREMENTS": MEASURED_RENEWABLE_INCREMENTS,
    "FORECAST_LOAD_INCREMENTS": FORECAST_LOAD_INCREMENTS,
    "FORECAST_RENEWABLE_INCREMENTS": FORECAST_RENEWABLE_INCREMENTS,
    "INITIAL_DISPATCHABLE_POWER": INITIAL_DISPATCHABLE_POWER,
    "dispatchable_capacities": dispatchable_capacities,
    "Q_cost": Q_cost,
    "R_cost": R_cost,
    "upper_bounds_states": upper_bounds_states,
    "lower_bounds_states": lower_bounds_states,
    "upper_bounds_inputs": upper_bounds_inputs,
    "lower_bounds_inputs": lower_bounds_inputs,
    "Weighted_Adjacency_Matrix": Weighted_Adjacency_Matrix,
    "Control_Agents": Control_Agents,
    "Augmented_Control_Agents": Augmented_Control_Agents,
    "Control_Agents_Matrices": Control_Agents_Matrices,
    "Control_Agents_Optimization_Matrices": Control_Agents_Optimization_Matrices,
    "Reference_Signal": Reference_Signal,
}



# %% MARK: Control Simulation

x_evolution, u_evolution, w_evolution = control_simulation(simulation_data) 


# %% MARK: Plot and Store Results

import matplotlib.pyplot as plt

simulation_time = np.arange(0, simulation_horizon+1)

fig_1, ax_1 = plt.subplots(figsize=(7, 4.5))
# plt.step(t_data, actual_total_load,where='post', label='Load measurement')
# plt.step(t_data, forecast_total_load,where='post', linestyle='--', label='Load forecast')
# plt.step(t_original, actual_total_load, where='post', color = 'blue', label='Load measurement')
# plt.step(t_original, forecast_total_load, where='post', color = 'green', linestyle='--', label='Load forecast')
for agent_Idx in range(number_atomic_agents):
    plt.step(simulation_time, x_evolution[agent_Idx*NUM_STATES, :], where='post', label= "Load measurement")
# plt.step(t_interpolation, forecast_total_load_interp, where='post', color = 'green', linestyle='--', label= "Load forecast")
ax_1.set_ylabel('Angle [deg]')
ax_1.set_xlabel(f'Time [s]')
ax_1.set_title(f'Control simulation -- Angle deviation')
# ax_1.legend()
ax_1.grid(True, linestyle='--', color='lightgrey')
# ax_1.set_xticks(np.arange(0, t_interpolation[-1]+1, 3*t_interpolation[-1]/number_hours))
ax_1.set_xlim(simulation_time[0], simulation_time[-1])
plt.tight_layout()
plt.show()


fig_2, ax_2 = plt.subplots(figsize=(7, 4.5))
# plt.step(t_data, actual_total_load,where='post', label='Load measurement')
# plt.step(t_data, forecast_total_load,where='post', linestyle='--', label='Load forecast')
# plt.step(t_original, actual_total_load, where='post', color = 'blue', label='Load measurement')
# plt.step(t_original, forecast_total_load, where='post', color = 'green', linestyle='--', label='Load forecast')
for agent_Idx in range(number_atomic_agents):
    plt.step(simulation_time[:], x_evolution[agent_Idx*NUM_STATES+1, :], where='post', label= "Load measurement")
# plt.step(t_interpolation, forecast_total_load_interp, where='post', color = 'green', linestyle='--', label= "Load forecast")
ax_2.set_ylabel('Hertz [HZ]')
ax_2.set_xlabel(f'Time [s]')
ax_2.set_title(f'Control simulation - Frequency deviation')
# ax_2.legend()
ax_2.grid(True, linestyle='--', color='lightgrey')
# ax_1.set_xticks(np.arange(0, t_interpolation[-1]+1, 3*t_interpolation[-1]/number_hours))
ax_2.set_xlim(simulation_time[0], simulation_time[-1])
plt.tight_layout()
plt.show()

fig_2, ax_2 = plt.subplots(figsize=(7, 4.5))
# plt.step(t_data, actual_total_load,where='post', label='Load measurement')
# plt.step(t_data, forecast_total_load,where='post', linestyle='--', label='Load forecast')
# plt.step(t_original, actual_total_load, where='post', color = 'blue', label='Load measurement')
# plt.step(t_original, forecast_total_load, where='post', color = 'green', linestyle='--', label='Load forecast')
for agent_Idx in range(number_atomic_agents):
    plt.step(simulation_time[:], x_evolution[agent_Idx*NUM_STATES+2, :], where='post', label= "Load measurement")
# plt.step(t_interpolation, forecast_total_load_interp, where='post', color = 'green', linestyle='--', label= "Load forecast")
ax_2.set_ylabel('Power [GW]')
ax_2.set_xlabel(f'Time [s]')
ax_2.set_title(f'Control simulation - ESS')
# ax_2.legend()
ax_2.grid(True, linestyle='--', color='lightgrey')
# ax_1.set_xticks(np.arange(0, t_interpolation[-1]+1, 3*t_interpolation[-1]/number_hours))
ax_2.set_xlim(simulation_time[0], simulation_time[-1])
plt.tight_layout()
plt.show()

fig_2, ax_2 = plt.subplots(figsize=(7, 4.5))
# plt.step(t_data, actual_total_load,where='post', label='Load measurement')
# plt.step(t_data, forecast_total_load,where='post', linestyle='--', label='Load forecast')
# plt.step(t_original, actual_total_load, where='post', color = 'blue', label='Load measurement')
# plt.step(t_original, forecast_total_load, where='post', color = 'green', linestyle='--', label='Load forecast')
for agent_Idx in range(number_atomic_agents):
    plt.step(simulation_time[:], x_evolution[agent_Idx*NUM_STATES+3, :], where='post', label= "Load measurement")
# plt.step(t_interpolation, forecast_total_load_interp, where='post', color = 'green', linestyle='--', label= "Load forecast")
ax_2.set_ylabel('Power [GW]')
ax_2.set_xlabel(f'Time [s]')
ax_2.set_title(f'Control simulation - Tie Lines')
# ax_2.legend()
ax_2.grid(True, linestyle='--', color='lightgrey')
# ax_1.set_xticks(np.arange(0, t_interpolation[-1]+1, 3*t_interpolation[-1]/number_hours))
ax_2.set_xlim(simulation_time[0], simulation_time[-1])
plt.tight_layout()
plt.show()

fig_2, ax_2 = plt.subplots(figsize=(7, 4.5))
# plt.step(t_data, actual_total_load,where='post', label='Load measurement')
# plt.step(t_data, forecast_total_load,where='post', linestyle='--', label='Load forecast')
# plt.step(t_original, actual_total_load, where='post', color = 'blue', label='Load measurement')
# plt.step(t_original, forecast_total_load, where='post', color = 'green', linestyle='--', label='Load forecast')
for agent_Idx in range(number_atomic_agents):
    plt.step(simulation_time[:], x_evolution[agent_Idx*NUM_STATES+4, :], where='post', label= "Load measurement")
# plt.step(t_interpolation, forecast_total_load_interp, where='post', color = 'green', linestyle='--', label= "Load forecast")
ax_2.set_ylabel('Power [GW]')
ax_2.set_xlabel(f'Time [s]')
ax_2.set_title(f'Control simulation - Total generated power')
# ax_2.legend()
ax_2.grid(True, linestyle='--', color='lightgrey')
# ax_1.set_xticks(np.arange(0, t_interpolation[-1]+1, 3*t_interpolation[-1]/number_hours))
ax_2.set_xlim(simulation_time[0], simulation_time[-1])
plt.tight_layout()
plt.show()


fig_3, ax_3 = plt.subplots(figsize=(7, 4.5))
# plt.step(t_data, actual_total_load,where='post', label='Load measurement')
# plt.step(t_data, forecast_total_load,where='post', linestyle='--', label='Load forecast')
# plt.step(t_original, actual_total_load, where='post', color = 'blue', label='Load measurement')
# plt.step(t_original, forecast_total_load, where='post', color = 'green', linestyle='--', label='Load forecast')
for agent_Idx in range(number_atomic_agents):
    plt.step(simulation_time, w_evolution[agent_Idx*2, :], where='post', label= "Load measurement")
# plt.step(t_interpolation, forecast_total_load_interp, where='post', color = 'green', linestyle='--', label= "Load forecast")
ax_3.set_ylabel('Power [GW]')
ax_3.set_xlabel(f'Time [s]')
ax_3.set_title(f'Control simulation - External signal w1')
# ax_3.legend()
ax_3.grid(True, linestyle='--', color='lightgrey')
# ax_1.set_xticks(np.arange(0, t_interpolation[-1]+1, 3*t_interpolation[-1]/number_hours))
ax_3.set_xlim(simulation_time[0], simulation_time[-1])
plt.tight_layout()
plt.show()

fig_3, ax_3 = plt.subplots(figsize=(7, 4.5))
# plt.step(t_data, actual_total_load,where='post', label='Load measurement')
# plt.step(t_data, forecast_total_load,where='post', linestyle='--', label='Load forecast')
# plt.step(t_original, actual_total_load, where='post', color = 'blue', label='Load measurement')
# plt.step(t_original, forecast_total_load, where='post', color = 'green', linestyle='--', label='Load forecast')
for agent_Idx in range(number_atomic_agents):
    plt.step(simulation_time, w_evolution[agent_Idx*2+1, :], where='post', label= "Load measurement")
# plt.step(t_interpolation, forecast_total_load_interp, where='post', color = 'green', linestyle='--', label= "Load forecast")
ax_3.set_ylabel('Power [GW]')
ax_3.set_xlabel(f'Time [s]')
ax_3.set_title(f'Control simulation - External signal w2')
# ax_3.legend()
ax_3.grid(True, linestyle='--', color='lightgrey')
# ax_1.set_xticks(np.arange(0, t_interpolation[-1]+1, 3*t_interpolation[-1]/number_hours))
ax_3.set_xlim(simulation_time[0], simulation_time[-1])
plt.tight_layout()
plt.show()


# %%
