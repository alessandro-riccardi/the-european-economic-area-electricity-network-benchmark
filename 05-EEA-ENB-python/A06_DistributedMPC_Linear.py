# %% 
# MARK: Reset Operations

from IPython import get_ipython
get_ipython().run_line_magic('reset', '-f')
# print("\n" * 100)

#  %%
# MARK: Options

EXPORT_DATA = False
DRAW_PLOTS = True
EXPORT_PLOTS = False

Simulation_ID = "DMPC_TEST"

# %% 
# MARK: Import Libraries

import numpy as np 
import pandas as pd
import gurobipy as gp
import os
if not os.path.exists("Output_Data"):
    os.mkdir("Output_Data")
if not os.path.exists("Input_Data"):
    os.mkdir("Input_Data")

INPUT_FOLDER = "Input_Data"
OUTPUT_FOLDER = "Output_Data"

import pickle as pk
import math as mt

import matplotlib.pyplot as plt

# Graphic library
import plotly.offline as pyo
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots  
import plotly.io as pio
#  Replace default graphic
pyo.init_notebook_mode(connected=True)
plotly_template = "plotly_white"
# plotly_template = "plotly_dark"

# random numbers
import random as rnd
# rnd.seed(1)

# For time tracking
import time as tm

# Support functions
from A00_Support_Functions import * 

# %%
# MARK: Electrical Areas
#  Select electrical areas to include in the simulation

# Select areas to simulate
# LIST_ELECTRICAL_AREAS = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
# LIST_ELECTRICAL_AREAS = [17, 2, 6, 10]
LIST_ELECTRICAL_AREAS = [17, 2]
# LIST_ELECTRICAL_AREAS = [9, 10, 26]
LIST_ELECTRICAL_AREAS.sort()
NUMBER_ATOMIC_AGENTS = len(LIST_ELECTRICAL_AREAS)

LIST_ATOMIC_AGENTS = create_empty_list(NUMBER_ATOMIC_AGENTS)
for i in range(0,NUMBER_ATOMIC_AGENTS):
    LIST_ATOMIC_AGENTS[i] = LIST_ELECTRICAL_AREAS[i] - 1

print("Electrical areas: ", LIST_ELECTRICAL_AREAS)
print("Atomic control agents: ", LIST_ATOMIC_AGENTS)

NUM_STATES = 5
NUM_INPUTS = 3


# %%
# MARK: System Parameters and Bounds

# Load capacities
DISPATCHABLE_CAPACITIES = np.loadtxt('Data/Capacities_List.csv', delimiter=',')

# TAU = 2.5
# The realistic situation is listed in the following. However, we simplify the simulation and consider only 200 steps in a hour instead of 1400. To use the realistic version, input data has to be reprocessed. You can use the dataset in the original version of the benchmark.
# STEPS_HOUR = 60*60/TAU

TAU = 2.5
STEPS_HOUR = 200

UPPER_BOUNDS_STATE = np.zeros((NUM_STATES,NUMBER_ATOMIC_AGENTS))
LOWER_BOUNDS_STATE = np.zeros((NUM_STATES,NUMBER_ATOMIC_AGENTS))
UPPER_BOUNDS_INPUT = np.zeros((NUM_INPUTS,NUMBER_ATOMIC_AGENTS))
LOWER_BOUNDS_INPUT = np.zeros((NUM_INPUTS,NUMBER_ATOMIC_AGENTS))

for i in range(0,NUMBER_ATOMIC_AGENTS):
    Agent_i_Idx = LIST_ATOMIC_AGENTS[i]
    UPPER_BOUNDS_STATE[:,i] = [3.5,                                              # Bound on Delta delta(k)
                               0.05,                                            # Bound on Delta f(k)
                               DISPATCHABLE_CAPACITIES[Agent_i_Idx]/1000,    # Bound on e(k) in [GW], assume = max dispatchale
                               0,                                               # Bound on PTie(k) (Undefined and unassgined)
                               DISPATCHABLE_CAPACITIES[Agent_i_Idx]/1000]       # Bound on Pdisp(k) in [GW]
    
    LOWER_BOUNDS_STATE[:,i] = [-3.5,
                               -0.05,
                               0,
                               0,
                               0]

    UPPER_BOUNDS_INPUT[:,i] = [DISPATCHABLE_CAPACITIES[Agent_i_Idx]/1000/STEPS_HOUR,     # Bound on Delta Pdisp(k) in [GW]
                               DISPATCHABLE_CAPACITIES[Agent_i_Idx]/1000/STEPS_HOUR,
                               DISPATCHABLE_CAPACITIES[Agent_i_Idx]/1000/STEPS_HOUR]     # Bound on PESS(k) in [GW]

    LOWER_BOUNDS_INPUT[:,i] = [-DISPATCHABLE_CAPACITIES[Agent_i_Idx]/1000/STEPS_HOUR,
                               0,
                               0]

# Realistic Case
NUMBER_OF_HOURS = 1
# SIMULATION_HORIZON = STEPS_HOUR*NUMBER_OF_HOURS + 1

# Simplified Case
SIMULATION_HORIZON = 1000 +1
PREDICTION_HORIZON = 10
EPSILON = 1e-10

# Cost matrices
Q = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,NUM_STATES*NUMBER_ATOMIC_AGENTS))
R = np.zeros((NUM_INPUTS*NUMBER_ATOMIC_AGENTS,NUM_INPUTS*NUMBER_ATOMIC_AGENTS))

Global_Idx_1 = 0
Global_Idx_2 = 0
for i in range(0,NUMBER_ATOMIC_AGENTS):
    Q[Global_Idx_1, Global_Idx_1] = 100
    Q[Global_Idx_1 + 1, Global_Idx_1 + 1] = 10
    Q[Global_Idx_1 + 2, Global_Idx_1 + 2] = 1
    Global_Idx_1 += NUM_STATES

    R[Global_Idx_2, Global_Idx_2] = 1
    R[Global_Idx_2 + 1, Global_Idx_2 + 1] = 1
    R[Global_Idx_2 + 2, Global_Idx_2 + 2] = 1
    Global_Idx_2 += 3

# %%
# MARK: Nominal Dynamics of the System

# Load full adjacency matrix
WEIGHTED_ADJACENCY_MATRIX_RAW = np.loadtxt('Data/Adj_W.csv', delimiter=',')

# Construct the weighted adjacency matrix
Weighted_Adjacency_Matrix = np.zeros((NUMBER_ATOMIC_AGENTS,NUMBER_ATOMIC_AGENTS))
for i in range(0,NUMBER_ATOMIC_AGENTS):
    Agent_i_idx = LIST_ATOMIC_AGENTS[i]
    for j in range(0,NUMBER_ATOMIC_AGENTS):
        Agent_j_idx = LIST_ATOMIC_AGENTS[j] 
        Weighted_Adjacency_Matrix[i,j] = WEIGHTED_ADJACENCY_MATRIX_RAW[Agent_i_idx,Agent_j_idx]

# Build system dynamics
A_Dynamics = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,NUM_STATES*NUMBER_ATOMIC_AGENTS))
B_Dynamics = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,NUM_INPUTS*NUMBER_ATOMIC_AGENTS))
# B_Dynamics_Nominal = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,NUM_INPUTS*NUMBER_ATOMIC_AGENTS))
D_Dynamics = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,2*NUMBER_ATOMIC_AGENTS))

Line_Impedance = 1 
Kp_i = 0.05
Tr_i = 25
Tt_i = 2.5

for i in range(0,NUMBER_ATOMIC_AGENTS):
    
    Kii = 0
    Lii = 0
    for j in range(0,NUMBER_ATOMIC_AGENTS):
        if Weighted_Adjacency_Matrix[i,j] != 0:
            Kii = Kii + (((TAU*Kp_i)/(Tr_i))*(Line_Impedance/Weighted_Adjacency_Matrix[i,j]))
            Lii = Lii + TAU * (Line_Impedance / Weighted_Adjacency_Matrix[i, j])

    A_i = [[1,    TAU*2*mt.pi,      0, 0, 0],
           [-Kii, (1 - (TAU/Tr_i)), 0, 0, 0],
           [0,    0,                1, 0, 0],
           [Lii, 0,                0, 1, 0], 
           [0,    0,                0, 0, 1]]

        
    # B_i_nominal = [[0,               0],
    #                [(Kp_i*TAU)/Tr_i, -(Kp_i*TAU)/Tr_i],
    #                [0,               1], # HERE THE VALUE MUST BE TAUS*ETA_i^j, BUT WE ASSING IT AFTERWARDS
    #                [0,               0],
    #                [TAU,               0]]
    
    ETA_c = 0.9
    ETA_d = 1/0.9

    B_i = [[0,               0,                0],
           [(Kp_i*TAU)/Tr_i, -(Kp_i*TAU)/Tr_i, (Kp_i*TAU)/Tr_i],
           [0,               TAU*ETA_c,        -TAU*ETA_d], 
           [0,               0,                0],
           [TAU,             0,                0]]
    
    D_i = [[0,                0],
           [-(Kp_i*TAU)/Tr_i, (Kp_i*TAU)/Tr_i],
           [0,                0],
           [0,                0],
           [0,                0]]
    
    A_Dynamics[i*NUM_STATES:(i+1)*NUM_STATES,i*NUM_STATES:(i+1)*NUM_STATES] = A_i.copy()
    B_Dynamics[i*NUM_STATES:(i+1)*NUM_STATES,i*NUM_INPUTS:(i+1)*NUM_INPUTS] = B_i.copy()
    # B_Dynamics_Nominal[i*NUM_STATES:(i+1)*NUM_STATES,i*NUM_INPUTS:(i+1)*NUM_INPUTS] = B_i_nominal.copy()
    D_Dynamics[i*NUM_STATES:(i+1)*NUM_STATES,i*2:(i+1)*2] = D_i.copy()

    for j in range(0,NUMBER_ATOMIC_AGENTS):
        if Weighted_Adjacency_Matrix[i,j] != 0:
            A_Dynamics[(i*NUM_STATES)+1,j*NUM_STATES] = ((TAU*Kp_i)/(Tr_i))*(Line_Impedance/Weighted_Adjacency_Matrix[i,j])
            A_Dynamics[(i*NUM_STATES)+3,j*NUM_STATES] = -TAU*(Line_Impedance/Weighted_Adjacency_Matrix[i,j])

# %%
# MARK: List of Parameters
PARAMETERS_LIST = [NUMBER_ATOMIC_AGENTS,    # 0
                   SIMULATION_HORIZON,      # 1
                   PREDICTION_HORIZON,      # 2
                   A_Dynamics,              # 3
                   B_Dynamics,      # 4
                   D_Dynamics,              # 5
                   UPPER_BOUNDS_INPUT,      # 6
                   LOWER_BOUNDS_INPUT,      # 7
                   UPPER_BOUNDS_STATE,      # 8
                   LOWER_BOUNDS_STATE,      # 9
                   Q,                       # 10
                   R,                       # 11
                   EPSILON,                 # 12
                   TAU]                     # 13


#%%
# MARK: Load External Signals

# Load signals
# Aggregated data
MEASURED_LOAD_NETWORK = np.loadtxt('Data/0A_MeasuredLoad_Faster.csv', delimiter=',')
MEASURED_RENEWABLE_NETWORK = np.loadtxt('Data/0B_MeasuredRenewable_Faster.csv', delimiter=',')

MEASURED_LOAD = np.zeros((NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+PREDICTION_HORIZON))
MEASURED_RENEWABLE = np.zeros((NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+PREDICTION_HORIZON))

# Incremental data
MEASURED_LOAD_INCREMENTS_NETWORK = np.loadtxt('Data/0E_MeasuredLoadIncrements_Faster.csv', delimiter=',')
MEASURED_RENEWABLE_INCREMENTS_NETWORK = np.loadtxt('Data/0F_MeasuredRenewableIncrements_Faster.csv', delimiter=',')

MEASURED_LOAD_INCREMENTS = np.zeros((NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+PREDICTION_HORIZON))
MEASURED_RENEWABLE_INCREMENTS = np.zeros((NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+PREDICTION_HORIZON))

FORECAST_LOAD_INCREMENTS_NETWORK = np.loadtxt('Data/0G_ForecastLoadIncrements_Faster.csv', delimiter=',')
FORECAST_RENEWABLE_INCREMENTS_NETWORK = np.loadtxt('Data/0H_ForecastRenewableIncrements_Faster.csv', delimiter=',')

FORECAST_LOAD_INCREMENTS = np.zeros((NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+PREDICTION_HORIZON))
FORECAST_RENEWABLE_INCREMENTS = np.zeros((NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+PREDICTION_HORIZON))

for i in range(0,NUMBER_ATOMIC_AGENTS):
    Agent_Idx = LIST_ATOMIC_AGENTS[i] 
    MEASURED_LOAD[i,:] = MEASURED_LOAD_NETWORK[Agent_Idx,0:SIMULATION_HORIZON+PREDICTION_HORIZON]
    MEASURED_RENEWABLE[i,:] = MEASURED_RENEWABLE_NETWORK[Agent_Idx,0:SIMULATION_HORIZON+PREDICTION_HORIZON]
    MEASURED_LOAD_INCREMENTS[i,:] = MEASURED_LOAD_INCREMENTS_NETWORK[Agent_Idx,0:SIMULATION_HORIZON+PREDICTION_HORIZON]
    MEASURED_RENEWABLE_INCREMENTS[i,:] = MEASURED_RENEWABLE_INCREMENTS_NETWORK[Agent_Idx,0:SIMULATION_HORIZON+PREDICTION_HORIZON]
    FORECAST_LOAD_INCREMENTS[i,:] = FORECAST_LOAD_INCREMENTS_NETWORK[Agent_Idx,0:SIMULATION_HORIZON+PREDICTION_HORIZON]
    FORECAST_RENEWABLE_INCREMENTS[i,:] = FORECAST_RENEWABLE_INCREMENTS_NETWORK[Agent_Idx,0:SIMULATION_HORIZON+PREDICTION_HORIZON]

# Dispatchable power at zero
INITIAL_DISPATCHABLE_POWER = np.loadtxt('Data/0I_DispatchablePower_zero.csv', delimiter=',')
INITIAL_DISPATCHABLE_POWER = (np.atleast_2d(INITIAL_DISPATCHABLE_POWER).T)

#%%
# MARK: Plot External Signals

#  Load data
if DRAW_PLOTS == True:
    Plot_Measured_Load = go.Figure(go.Scatter(x=np.arange(0,SIMULATION_HORIZON), y=MEASURED_LOAD[0,:], name=f"Pload_{LIST_ELECTRICAL_AREAS[0]}", mode='lines'))

    for q in range(1,NUMBER_ATOMIC_AGENTS):
        Plot_Measured_Load.add_scatter(x=np.arange(0,SIMULATION_HORIZON), y=MEASURED_LOAD[q,:], name=f"Pload_{LIST_ELECTRICAL_AREAS[q]}", mode='lines')

    Plot_Measured_Load.update_layout(title="Measured load", title_x=0.5, 
                    xaxis_title="Time step k", yaxis_title="Pdisp(k)", template=plotly_template, width=800, height=500)  
    
    Plot_Measured_Load.show()

#  Renewable data
if DRAW_PLOTS == True:
    Plot_Measured_Renewable = go.Figure(go.Scatter(x=np.arange(0,SIMULATION_HORIZON), y=MEASURED_RENEWABLE[0,:], name=f"Pren_{LIST_ELECTRICAL_AREAS[0]}", mode='lines'))

    for q in range(1,NUMBER_ATOMIC_AGENTS):
        Plot_Measured_Renewable.add_scatter(x=np.arange(0,SIMULATION_HORIZON), y=MEASURED_RENEWABLE[q,:], name=f"Pren_{LIST_ELECTRICAL_AREAS[q]}", mode='lines')

    Plot_Measured_Renewable.update_layout(title="Measured renewable", title_x=0.5, 
                    xaxis_title="Time step k", yaxis_title="Pren(k)", template=plotly_template, width=800, height=500)  
    
    Plot_Measured_Renewable.show()

#  Load increments
if DRAW_PLOTS == True:
    Plot_Measured_Load_Increments = go.Figure(go.Scatter(x=np.arange(0,SIMULATION_HORIZON), y=MEASURED_LOAD_INCREMENTS[0,:], name=f"Delta Pload_{LIST_ELECTRICAL_AREAS[0]}", mode='lines'))

    for q in range(1,NUMBER_ATOMIC_AGENTS):
        Plot_Measured_Load_Increments.add_scatter(x=np.arange(0,SIMULATION_HORIZON), y=MEASURED_LOAD_INCREMENTS[q,:], name=f"Delta Pload_{LIST_ELECTRICAL_AREAS[q]}", mode='lines')

    Plot_Measured_Load_Increments.update_layout(title="Measured load increments", title_x=0.5, 
                    xaxis_title="Time step k", yaxis_title="Delta Pload(k)", template=plotly_template, width=800, height=500)  
    
    Plot_Measured_Load_Increments.show()

#  Renewable increments
if DRAW_PLOTS == True:
    Plot_Measured_Renewable_Increments = go.Figure(go.Scatter(x=np.arange(0,SIMULATION_HORIZON), y=MEASURED_RENEWABLE_INCREMENTS[0,:], name=f"Delta Pren_{LIST_ELECTRICAL_AREAS[0]}", mode='lines'))

    for q in range(1,NUMBER_ATOMIC_AGENTS):
        Plot_Measured_Renewable_Increments.add_scatter(x=np.arange(0,SIMULATION_HORIZON), y=MEASURED_RENEWABLE_INCREMENTS[q,:], name=f"Delta Pren_{LIST_ELECTRICAL_AREAS[q]}", mode='lines')

    Plot_Measured_Renewable_Increments.update_layout(title="Measured renewable increments", title_x=0.5, 
                    xaxis_title="Time step k", yaxis_title="Delta Pren(k)", template=plotly_template, width=800, height=500)  
    
    Plot_Measured_Renewable_Increments.show()

# %% 
# MARK: Reference Generator

Reference_Signal = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+PREDICTION_HORIZON))

# This is to set a certain desired value for the ESS charge and used to test the hybrid configuration
for j in range(0,SIMULATION_HORIZON+PREDICTION_HORIZON):
    Row_Idx = 2
    for i in range(0,NUMBER_ATOMIC_AGENTS): 
        Row_Idx += NUM_STATES

#%%
# MARK: Mixed Logical Dynamical System Matrices Formulation

# A_MLD = A_Dynamics.copy()
# Bu_MLD_Nominal = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,NUM_INPUTS*NUMBER_ATOMIC_AGENTS))
# Bu_MLD = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,NUMBER_ATOMIC_AGENTS))
# Bz_MLD = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,8*NUMBER_ATOMIC_AGENTS))
# D_MLD = D_Dynamics .copy()

# for i in range(0,NUMBER_ATOMIC_AGENTS):
#     Bu_MLD[(i*NUM_STATES)+1,i] = B_Dynamics_Nominal[(i*NUM_STATES)+1,2*i].copy()        
#     Bu_MLD[(i*NUM_STATES)+4,i] = B_Dynamics_Nominal[(i*NUM_STATES)+4,2*i].copy()    
#     Bu_MLD_Nominal[(i*NUM_STATES)+1,:] = B_Dynamics_Nominal[(i*NUM_STATES)+1,:].copy()     
#     Bu_MLD_Nominal[(i*NUM_STATES)+2,1] = TAU
#     Bu_MLD_Nominal[(i*NUM_STATES)+4,:] = B_Dynamics_Nominal[(i*NUM_STATES)+4,:].copy() 
#     # Bz_MLD[(i*NUM_STATES)+2,(i*8):(i+1)*8] = [TAU, TAU, TAU, TAU, TAU, TAU, TAU, TAU]
#     Bz_MLD[(i*NUM_STATES)+2,(i*8):(i+1)*8] = [TAU*0.9, TAU*0.7, TAU*0.5, TAU*0.3, TAU*(1/0.9), TAU*(1/0.7), TAU*(1/0.5), TAU*(1/0.3)]

# %%
# MARK: Control Agents Definition and Associated Augmented Control Agents

# Select one of the optimion below, or pass a selection of control agents directly obtained from partitioning
#####################################################################
# Option 1
# # Creation of a single agent comprehending the entire network
# Control_Agents = create_empty_list(1)
# for i in range(0,NUMBER_ATOMIC_AGENTS):
#     Control_Agents[0].append(LIST_ATOMIC_AGENTS[i])
# print("Control agents: ", Control_Agents)
# Augmented_Control_Agents = Control_Agents.copy()
# Augmented_Control_Agents[0].sort()
# print("Augmented control agent ", 0, " : ", Augmented_Control_Agents[0])

#####################################################################

#####################################################################
# Option 2
# Creation of individual agent, one for each element of the network
Control_Agents = create_empty_list(NUMBER_ATOMIC_AGENTS)
for i in range(0,NUMBER_ATOMIC_AGENTS):
    Control_Agents[i].append(LIST_ATOMIC_AGENTS[i])
#####################################################################

#####################################################################
# Option 3
# Optimization based partitioning from matlab
# Cerate a user defined partitoining of the agents
####################################################################

NUMBER_CONTROL_AGENTS = len(Control_Agents)

print("Control agents: ", Control_Agents)
print("Number control agents: ", NUMBER_CONTROL_AGENTS)

#########################################################################
# DO NOT USE IN COMBIATION WITH SINGLE AGENT
# Augmented control agents creation
Augmented_Control_Agents = Control_Agents.copy()
# for l in range(0,NUMBER_CONTROL_AGENTS):
#     Augmented_Control_Agents[l] = Control_Agents[l].copy()
#     Size_Control_Agent = len(Control_Agents[l])
    
#     for i in range(0,NUMBER_ATOMIC_AGENTS):
#         if LIST_ATOMIC_AGENTS[i] in Control_Agents[l]:
#             for j in range(0,NUMBER_ATOMIC_AGENTS):
#                 if (Weighted_Adjacency_Matrix[i,j] != 0) and (LIST_ATOMIC_AGENTS[j] not in Control_Agents[l]):
#                     Augmented_Control_Agents[l].append(LIST_ATOMIC_AGENTS[j])
    
#     Augmented_Control_Agents[l] = list(set(Augmented_Control_Agents[l]))
#     Augmented_Control_Agents[l].sort()
#     print("Augmented control agent ", l, " : ", Augmented_Control_Agents[l])

# %% 
# MARK: Contruction of the Augmented Control Agents Matrices

Control_Agents_Matrices = create_empty_list_2D(NUMBER_CONTROL_AGENTS, 7)

for l in range(0,NUMBER_CONTROL_AGENTS):

    Size_Augmented_Control_Agent = len(Augmented_Control_Agents[l])
    
    A_Augmented = np.zeros((NUM_STATES*Size_Augmented_Control_Agent,NUM_STATES*Size_Augmented_Control_Agent))
    B_Augmented = np.zeros((NUM_STATES*Size_Augmented_Control_Agent,NUM_INPUTS*Size_Augmented_Control_Agent))
    # Bu_Augmented = np.zeros((NUM_STATES*Size_Augmented_Control_Agent,Size_Augmented_Control_Agent))
    # Bz_Augmented = np.zeros((NUM_STATES*Size_Augmented_Control_Agent,8*Size_Augmented_Control_Agent))
    D_Augmented = np.zeros((NUM_STATES*Size_Augmented_Control_Agent,2*Size_Augmented_Control_Agent))
    Q_Augmented = np.zeros((NUM_STATES*Size_Augmented_Control_Agent,NUM_STATES*Size_Augmented_Control_Agent))
    R_Augmented = np.zeros((NUM_INPUTS*Size_Augmented_Control_Agent,NUM_INPUTS*Size_Augmented_Control_Agent))

    for i in range(0, Size_Augmented_Control_Agent):
        Agent_Index_1 = LIST_ATOMIC_AGENTS.index(Augmented_Control_Agents[l][i])
        for j in range(0, Size_Augmented_Control_Agent):
            Agent_Index_2 = LIST_ATOMIC_AGENTS.index(Augmented_Control_Agents[l][j])
            A_Augmented[i*NUM_STATES:(i+1)*NUM_STATES,j*NUM_STATES:(j+1)*NUM_STATES] = A_Dynamics[Agent_Index_1*NUM_STATES:(Agent_Index_1+1)*NUM_STATES,Agent_Index_2*NUM_STATES:(Agent_Index_2+1)*NUM_STATES].copy()
            B_Augmented[i*NUM_STATES:(i+1)*NUM_STATES,j*NUM_INPUTS:(j+1)*NUM_INPUTS] = B_Dynamics[Agent_Index_1*NUM_STATES:(Agent_Index_1+1)*NUM_STATES, Agent_Index_2*NUM_INPUTS:(Agent_Index_2+1)*NUM_INPUTS].copy()
            # Bu_Augmented[i*NUM_STATES:(i+1)*NUM_STATES,j] = Bu_MLD[Agent_Index_1*NUM_STATES:(Agent_Index_1+1)*NUM_STATES, Agent_Index_2].copy()
            # Bz_Augmented[i*NUM_STATES:(i+1)*NUM_STATES,j*8:(j+1)*8] = Bz_MLD[Agent_Index_1*NUM_STATES:(Agent_Index_1+1)*NUM_STATES,Agent_Index_2*8:(Agent_Index_2+1)*8].copy()
            D_Augmented[i*NUM_STATES:(i+1)*NUM_STATES,j*2:(j+1)*2] = D_Dynamics[Agent_Index_1*NUM_STATES:(Agent_Index_1+1)*NUM_STATES,Agent_Index_2*2:(Agent_Index_2+1)*2].copy()
            Q_Augmented[i*NUM_STATES:(i+1)*NUM_STATES,j*NUM_STATES:(j+1)*NUM_STATES] = Q[Agent_Index_1*NUM_STATES:(Agent_Index_1+1)*NUM_STATES,Agent_Index_2*NUM_STATES:(Agent_Index_2+1)*NUM_STATES].copy()
            R_Augmented[i*NUM_INPUTS:(i+1)*NUM_INPUTS,j*NUM_INPUTS:(j+1)*NUM_INPUTS] = R[Agent_Index_1*NUM_INPUTS:(Agent_Index_1+1)*NUM_INPUTS,Agent_Index_2*NUM_INPUTS:(Agent_Index_2+1)*NUM_INPUTS].copy()
            # R_Augmented[i,j] = R[Agent_Index_1, Agent_Index_2].copy()
    
    Control_Agents_Matrices[l][0] = A_Augmented.copy()
    Control_Agents_Matrices[l][1] = B_Augmented.copy()
    Control_Agents_Matrices[l][2] = Q_Augmented.copy()
    Control_Agents_Matrices[l][3] = R_Augmented.copy()
    # Control_Agents_Matrices[l][4] = Bz_Augmented.copy()
    Control_Agents_Matrices[l][5] = D_Augmented.copy()
    Control_Agents_Matrices[l][6] = B_Augmented.copy()

#%%
# MARK: Build Optimization Matrices

Control_Agents_Optimization_Matrices = create_empty_list_2D(NUMBER_CONTROL_AGENTS, 8)

for l in range(0,NUMBER_CONTROL_AGENTS):
    Size_Augmented_Control_Agent = len(Augmented_Control_Agents[l])

    M_Optimization = np.zeros((NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON,NUM_STATES*Size_Augmented_Control_Agent), dtype=np.float64)
    C_Optimization = np.zeros((NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON,NUM_INPUTS*Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)
    # Cu_Optimization = np.zeros((NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON,Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)
    # Cz_Optimization = np.zeros((NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON,8*Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)
    D_Optimization = np.zeros((NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON,2*Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)

    A_Augmented = Control_Agents_Matrices[l][0].copy()
    B_Augmented = Control_Agents_Matrices[l][1].copy()
    # Bu_Augmented = Control_Agents_Matrices[l][1].copy()
    # Bz_Augmented = Control_Agents_Matrices[l][4].copy()
    D_Augmented = Control_Agents_Matrices[l][5].copy()

    Row_Index = 0
    for i in range(1,PREDICTION_HORIZON+1):

        M_Optimization[Row_Index:Row_Index+NUM_STATES*Size_Augmented_Control_Agent,:] = np.linalg.matrix_power(A_Augmented,i)
        
        Col_Index_1 = 0
        Col_Index_2 = 0
        Col_Index_3 = 0
        Col_Index_4 = 0
        for j in reversed(range(0,i)):
            C_Optimization[Row_Index:Row_Index+NUM_STATES*Size_Augmented_Control_Agent,Col_Index_1:Col_Index_1+NUM_INPUTS*Size_Augmented_Control_Agent] = np.linalg.matrix_power(A_Augmented,j) @ B_Augmented
            # C_Optimization[Row_Index:Row_Index+NUM_STATES*Size_Augmented_Control_Agent,Col_Index_2:Col_Index_2+Size_Augmented_Control_Agent] = np.linalg.matrix_power(A_Augmented,j) @ B_Augmented
            # Cz_Optimization[Row_Index:Row_Index+NUM_STATES*Size_Augmented_Control_Agent,Col_Index_3:Col_Index_3+8*Size_Augmented_Control_Agent] = np.linalg.matrix_power(A_Augmented,j) @ Bz_Augmented
            D_Optimization[Row_Index:Row_Index+NUM_STATES*Size_Augmented_Control_Agent,Col_Index_4:Col_Index_4+2*Size_Augmented_Control_Agent] = np.linalg.matrix_power(A_Augmented,j) @ D_Augmented
            Col_Index_4 += 2*Size_Augmented_Control_Agent
            Col_Index_1 += NUM_INPUTS*Size_Augmented_Control_Agent
            Col_Index_2 += Size_Augmented_Control_Agent
            Col_Index_3 += 8*Size_Augmented_Control_Agent
            # print(j)

        Row_Index = Row_Index + NUM_STATES*Size_Augmented_Control_Agent
    
    Control_Agents_Optimization_Matrices[l][0] = M_Optimization.copy()
    Control_Agents_Optimization_Matrices[l][1] = C_Optimization.copy()
    # Control_Agents_Optimization_Matrices[l][4] = Cz_Optimization.copy()
    Control_Agents_Optimization_Matrices[l][5] = D_Optimization.copy()
    # Control_Agents_Optimization_Matrices[l][6] = C_Optimization.copy()
    
    Q_Augmented = Control_Agents_Matrices[l][2].copy()
    R_Augmented = Control_Agents_Matrices[l][3].copy()

    Q_Optimization = np.zeros((NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON,NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)
    R_Optimization = np.zeros((NUM_INPUTS*Size_Augmented_Control_Agent*PREDICTION_HORIZON,NUM_INPUTS*Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)
    # R_Optimization_PWA = np.zeros((NUM_INPUTS*Size_Augmented_Control_Agent*PREDICTION_HORIZON,NUM_INPUTS*Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)

    Pos_Index = 0
    for i in range(0,PREDICTION_HORIZON):
        Q_Optimization[Pos_Index:Pos_Index+NUM_STATES*Size_Augmented_Control_Agent,Pos_Index:Pos_Index+NUM_STATES*Size_Augmented_Control_Agent] = Q_Augmented.copy()
        Pos_Index = Pos_Index + NUM_STATES*Size_Augmented_Control_Agent

    Pos_Index = 0
    for i in range(0,PREDICTION_HORIZON):
        R_Optimization[Pos_Index:Pos_Index+NUM_INPUTS*Size_Augmented_Control_Agent,Pos_Index:Pos_Index+NUM_INPUTS*Size_Augmented_Control_Agent] = R_Augmented.copy()
        Pos_Index = Pos_Index + NUM_INPUTS*Size_Augmented_Control_Agent

    # R_Optimization = np.zeros((NUM_INPUTS*PREDICTION_HORIZON*Size_Augmented_Control_Agent,NUM_INPUTS*PREDICTION_HORIZON*Size_Augmented_Control_Agent))
    # for i in range(0,len(R_Optimization)):
    #     R_Optimization[i,i] = 1
    
    # for i in range(0,len(R_Optimization_PWA)):
    #     R_Optimization_PWA[i,i] = 1

    Control_Agents_Optimization_Matrices[l][2] = Q_Optimization.copy()
    Control_Agents_Optimization_Matrices[l][3] = R_Optimization.copy()
    # Control_Agents_Optimization_Matrices[l][7] = R_Optimization_PWA.copy()

# %%
# MARK: Control simulation

# Preallocation of variables
x_evolution = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+1))
u_evolution = np.zeros((NUM_INPUTS*NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+1))
w_evolution = np.zeros((2*NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+1))

w_measured = np.zeros((2*NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+1))
w_forecast = np.zeros((2*NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+1))
# z_evolution = np.zeros((8*NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+1))
# d_evolution = np.zeros((8*NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+1))




#  Construction of the external signal
for k in range(0,SIMULATION_HORIZON+1):
    for i in range(0,NUMBER_ATOMIC_AGENTS):
        w_measured[i*2:(i+1)*2,k] = np.array([MEASURED_LOAD_INCREMENTS[i,k],MEASURED_RENEWABLE_INCREMENTS[i,k]])
        # Difference between measured and forecast
        # if k == 0:
        #     w_evolution[i*2:(i+1)*2,k] = np.array([MEASURED_LOAD_INCREMENTS[i,k],MEASURED_RENEWABLE_INCREMENTS[i,k]])
        # else:
        #     w_evolution[i*2:(i+1)*2,k] = np.array([FORECAST_LOAD_INCREMENTS[i,k],FORECAST_RENEWABLE_INCREMENTS[i,k]])
        # Only measured
        w_evolution[i*2:(i+1)*2,k] = np.array([MEASURED_LOAD_INCREMENTS[i,k],MEASURED_RENEWABLE_INCREMENTS[i,k]])


# # PREPROCESSING BOUNDS
Initial_Dispatchable_Power_Processed = np.zeros((NUMBER_ATOMIC_AGENTS,1))
for i in range(0,NUMBER_ATOMIC_AGENTS):
    Agent_Idx = LIST_ATOMIC_AGENTS[i]
    if(INITIAL_DISPATCHABLE_POWER[Agent_Idx,0] >= 3*UPPER_BOUNDS_STATE[4,i]/4):
        Initial_Dispatchable_Power_Processed[i,0] = 3*UPPER_BOUNDS_STATE[4,i]/4
    else:
        Initial_Dispatchable_Power_Processed[i,0] = INITIAL_DISPATCHABLE_POWER[Agent_Idx,0]
    
#  Initial state for the dipatchable generation
for i in range(0,NUMBER_ATOMIC_AGENTS):
    x_evolution[(i*NUM_STATES)+4,0] = Initial_Dispatchable_Power_Processed[i,0]

residual_norm = np.zeros((NUMBER_CONTROL_AGENTS))
Total_Core_Seconds = 0
Core_Seconds = create_empty_list(SIMULATION_HORIZON)
# max_number_of_iterations = 100
max_number_of_iterations = 1

residual_evolution = np.zeros((max_number_of_iterations))

for i in range(0, SIMULATION_HORIZON):
    Core_Seconds[i] = np.zeros((NUMBER_CONTROL_AGENTS,max_number_of_iterations))

rho = 0.01
# rho = 0.1
################################## BEST RESULTS
epsilon_convergence = 0.001
################################## COMPROMISE FOR SPEED
# epsilon_convergence = 0.01

u_local = create_empty_list(NUMBER_CONTROL_AGENTS)
x_local = create_empty_list(NUMBER_CONTROL_AGENTS)

u_avarage_local = np.zeros((NUM_INPUTS*NUMBER_ATOMIC_AGENTS, PREDICTION_HORIZON))
x_avarage_local = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS, PREDICTION_HORIZON))

consensus_variable = create_empty_list(NUMBER_CONTROL_AGENTS)
avarage_variable = create_empty_list(NUMBER_CONTROL_AGENTS)
avarage_variable_old = create_empty_list(NUMBER_CONTROL_AGENTS)
gamma = create_empty_list(NUMBER_CONTROL_AGENTS)


for l in range(0,NUMBER_CONTROL_AGENTS):
    number_of_agents_l = len(Augmented_Control_Agents[l])
    
    avarage_variable[l] = np.zeros(((NUM_STATES+NUM_INPUTS)*number_of_agents_l*PREDICTION_HORIZON,1))
    consensus_variable[l] = np.zeros(((NUM_STATES+NUM_INPUTS)*number_of_agents_l*PREDICTION_HORIZON,1))
    gamma[l] = np.zeros(((NUM_STATES+NUM_INPUTS)*number_of_agents_l*PREDICTION_HORIZON,1))

Simulation_Start_Time_Holder = tm.time()
Simulation_Timer_Start = tm.time()
# Simulation 
for k in range(0,SIMULATION_HORIZON):
    
    print("TIME STEP ", k)
    number_of_iterations = 0
    norm_codition_1 = False
    norm_codition_2 = False
    norm_codition_3 = False
    
    Core_Seconds_Control_Agent = np.zeros(NUMBER_CONTROL_AGENTS)

    while (number_of_iterations < max_number_of_iterations) and (norm_codition_1 == False) and (norm_codition_2 == False):

        print("Local iteration ", number_of_iterations + 1)

        for l in range(0,len(Augmented_Control_Agents)):
            Start_Time_Holder = tm.time()
            number_of_agents_l = len(Augmented_Control_Agents[l])
            
            #  Avarage variable store for norm evaluation
            avarage_variable_old[l] = avarage_variable[l].copy()

            # Local optimization matrices
            M_Optimization = Control_Agents_Optimization_Matrices[l][0].copy()
            C_Optimization = Control_Agents_Optimization_Matrices[l][1].copy()
            # Cu_Optimization = Control_Agents_Optimization_Matrices[l][1].copy()
            # Cz_Optimization = Control_Agents_Optimization_Matrices[l][4].copy()
            D_Optimization = Control_Agents_Optimization_Matrices[l][5].copy()
            Q_Optimization = Control_Agents_Optimization_Matrices[l][2].copy()
            R_Optimization = Control_Agents_Optimization_Matrices[l][3].copy() 
            # R_Optimization_PWA = Control_Agents_Optimization_Matrices[l][7].copy() 

             #  Model initialization
            gurobi_model = gp.Model("MPC_Local")

            #  State at k and reference for the agent
            x_k_l = np.zeros((NUM_STATES*number_of_agents_l,1))
            reference_k_l = np.zeros((NUM_STATES*number_of_agents_l*PREDICTION_HORIZON,1))
            external_signals_k_l = np.zeros((2*number_of_agents_l*PREDICTION_HORIZON,1))

            Global_Idx = 0
            for j in range(0,PREDICTION_HORIZON):
                for i in range(0,NUMBER_ATOMIC_AGENTS):
                    if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
                        reference_k_l[Global_Idx:Global_Idx+5,0] = Reference_Signal[i*5:(i+1)*5,k+j].copy()
                        Global_Idx += 5

            # d_l = np.zeros((2*number_of_agents_l,PREDICTION_HORIZON))

            Global_Idx = 0
            
            # Collecting the initial state from the global state evolution vector
            for i in range(0,NUMBER_ATOMIC_AGENTS):
                if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
                    x_k_l[Global_Idx*NUM_STATES:(Global_Idx+1)*NUM_STATES,0] = x_evolution[i*NUM_STATES:(i+1)*NUM_STATES,k].copy()
                    
                    Global_Idx += 1

            # Collecting the external signals for optimization signal and external signal for dynamics
            # Global_Idx = 0
            # for j in range(0, PREDICTION_HORIZON):
            #     for i in range(0,NUMBER_ATOMIC_AGENTS):
            #         if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
            #             external_signals_k_l[Global_Idx*2:(Global_Idx+1)*2,0] = np.array([MEASURED_LOAD_INCREMENTS[i,k+j],
            #                                                                               MEASURED_RENEWABLE_INCREMENTS[i,k+j]])
            #             Global_Idx += 1
            # distinguishiong between measured and forecast
            Global_Idx = 0
            for j in range(0, PREDICTION_HORIZON):
                for i in range(0,NUMBER_ATOMIC_AGENTS):
                    if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
                        if j == 0:
                            external_signals_k_l[Global_Idx*2:(Global_Idx+1)*2,0] = np.array([MEASURED_LOAD_INCREMENTS[i,k+j],
                                                                                            MEASURED_RENEWABLE_INCREMENTS[i,k+j]])
                            Global_Idx += 1
                        else:
                            external_signals_k_l[Global_Idx*2:(Global_Idx+1)*2,0] = np.array([FORECAST_LOAD_INCREMENTS[i,k+j],
                                                                                            FORECAST_RENEWABLE_INCREMENTS[i,k+j]])
                            Global_Idx += 1
            
            # Input bounds contruction
            Lower_Bounds_u = np.zeros((NUM_INPUTS*number_of_agents_l*PREDICTION_HORIZON,1))
            Upper_Bounds_u = np.zeros((NUM_INPUTS*number_of_agents_l*PREDICTION_HORIZON,1))
            # Lower_Bounds_z = np.zeros((8*number_of_agents_l*PREDICTION_HORIZON,1))
            # Upper_Bounds_z = np.zeros((8*number_of_agents_l*PREDICTION_HORIZON,1))

            # Lower_Bounds_u_PWA = np.zeros((NUM_INPUTS*number_of_agents_l*PREDICTION_HORIZON,1))
            # Upper_Bounds_u_PWA = np.zeros((NUM_INPUTS*number_of_agents_l*PREDICTION_HORIZON,1))
            
            # Construction of bounds for the input over the horizon from indivifual bounds
            Global_Idx_1 = 0
            # Global_Idx_2 = 0
            # Global_Idx_3 = 0
            for j in range(0,PREDICTION_HORIZON):
                for i in range(0,NUMBER_ATOMIC_AGENTS):
                    if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:

                        Lower_Bounds_u[Global_Idx_1,0] = LOWER_BOUNDS_INPUT[0,i]
                        Upper_Bounds_u[Global_Idx_1,0] = UPPER_BOUNDS_INPUT[0,i]
                        Lower_Bounds_u[Global_Idx_1+1,0] = LOWER_BOUNDS_INPUT[1,i]
                        Upper_Bounds_u[Global_Idx_1+1,0] = UPPER_BOUNDS_INPUT[1,i]
                        Lower_Bounds_u[Global_Idx_1+2,0] = LOWER_BOUNDS_INPUT[2,i]
                        Upper_Bounds_u[Global_Idx_1+2,0] = UPPER_BOUNDS_INPUT[2,i]

                        # Lower_Bounds_u_PWA[Global_Idx_3,0] = LOWER_BOUNDS_INPUT[0,i]
                        # Upper_Bounds_u_PWA[Global_Idx_3,0] = UPPER_BOUNDS_INPUT[0,i]
                        # Lower_Bounds_u_PWA[Global_Idx_3+1,0] = LOWER_BOUNDS_INPUT[1,i]
                        # Upper_Bounds_u_PWA[Global_Idx_3+1,0] = UPPER_BOUNDS_INPUT[1,i]
                        # for m in range(0,8):
                        #     Lower_Bounds_z[Global_Idx_2 + m,0] = LOWER_BOUNDS_INPUT[1,i]
                        #     Upper_Bounds_z[Global_Idx_2 + m,0] = UPPER_BOUNDS_INPUT[1,i]
                        
            
                        Global_Idx_1 += 3
                        # Global_Idx_2 += 8
                        # Global_Idx_3 += 2
 
            # Variables
            u_tilde_k = gurobi_model.addMVar((NUM_INPUTS*number_of_agents_l*PREDICTION_HORIZON, 1), lb = Lower_Bounds_u, ub = Upper_Bounds_u)
            # u_tilde_k_Pdis = gurobi_model.addMVar((number_of_agents_l*PREDICTION_HORIZON, 1), lb = Lower_Bounds_u, ub = Upper_Bounds_u)
            # u_tilde_k_PESS = gurobi_model.addMVar((number_of_agents_l*PREDICTION_HORIZON, 1), lb = Lower_Bounds_u, ub = Upper_Bounds_u)
            # z_tilde_k = gurobi_model.addMVar((8*number_of_agents_l*PREDICTION_HORIZON, 1), lb = Lower_Bounds_z, ub = Upper_Bounds_z)
            # d_tilde_k = gurobi_model.addMVar((8*number_of_agents_l*PREDICTION_HORIZON, 1), vtype=gp.GRB.BINARY)

            # for i in range(0,number_of_agents_l*PREDICTION_HORIZON):
            #     gurobi_model.addConstr(u_tilde_k_Pdis[i] == u_tilde_k[2*i])
            #     gurobi_model.addConstr(u_tilde_k_PESS[i] == u_tilde_k[(2*i)+1])



            # State variable update as a function of optimization variables to implement explicit formulation
            x_tilde_k = M_Optimization @ x_k_l + C_Optimization @ u_tilde_k + D_Optimization @ external_signals_k_l

            # Eta = np.array([0.9, 0.7, 0.5, 0.3, 1/0.9, 1/0.7, 1/0.5, 1/0.3])

            # MARK: Blocking
            #  For N = 30
            # gurobi_model.addConstr(u_tilde_k[2*number_of_agents_l*int(2*PREDICTION_HORIZON/6):2*number_of_agents_l*int(3*PREDICTION_HORIZON/6)] == u_tilde_k[2*number_of_agents_l*int(3*PREDICTION_HORIZON/6):2*number_of_agents_l*int(4*PREDICTION_HORIZON/6)])
            # gurobi_model.addConstr(u_tilde_k[2*number_of_agents_l*int(4*PREDICTION_HORIZON/6):2*number_of_agents_l*int(5*PREDICTION_HORIZON/6)] == u_tilde_k[2*number_of_agents_l*int(5*PREDICTION_HORIZON/6):2*number_of_agents_l*int(6*PREDICTION_HORIZON/6)])
            
            # Constraints on the state
            Global_Idx = 0
            for j in range(0,PREDICTION_HORIZON):
                for i in range(0,NUMBER_ATOMIC_AGENTS):
                    if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
                        
                        gurobi_model.addConstr(x_tilde_k[Global_Idx] <= UPPER_BOUNDS_STATE[0,i])
                        gurobi_model.addConstr(x_tilde_k[Global_Idx] >= LOWER_BOUNDS_STATE[0,i])

                        gurobi_model.addConstr(x_tilde_k[Global_Idx+1] <= UPPER_BOUNDS_STATE[1,i])
                        gurobi_model.addConstr(x_tilde_k[Global_Idx+1] >= LOWER_BOUNDS_STATE[1,i])

                        gurobi_model.addConstr(x_tilde_k[Global_Idx+2] <= UPPER_BOUNDS_STATE[2,i])
                        gurobi_model.addConstr(x_tilde_k[Global_Idx+2] >= 0)

                        gurobi_model.addConstr(x_tilde_k[Global_Idx+4] <= UPPER_BOUNDS_STATE[4,i])
                        gurobi_model.addConstr(x_tilde_k[Global_Idx+4] >= 0)

                        Global_Idx += 5

            # Constraints on delta
            #  Only one delta = 1 for each agent, at each time step
            # Global_Idx_3 = 0
            # for j in range(0,PREDICTION_HORIZON):
            #     Sum_Deltas = 0
            #     for m in range(0,8):
            #         Sum_Deltas = Sum_Deltas + d_tilde_k[Global_Idx_3 + m]
            #     gurobi_model.addConstr(Sum_Deltas == 1)
            #     Global_Idx_3 += 8

            # Constraints on auxiliary variables
            # Global_Idx_1 = 0
            # Global_Idx_2 = 0
            # for j in range(0,PREDICTION_HORIZON):
            #     for i in range(0,NUMBER_ATOMIC_AGENTS):
            #         if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:

            #             # Auxiliary variables bounds
            #             P_ESS_i_MAX = UPPER_BOUNDS_INPUT[1,i]
            #             P_ESS_i_min = LOWER_BOUNDS_INPUT[1,i]

            #             # PESS Construction for bounds
            #             PESS = 0
            #             for m in range(0,8):
            #                 PESS = PESS + (z_tilde_k[Global_Idx_1 + m]/Eta[m])


            #             # Contraints connection

            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1])
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+1] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+1])
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+2] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+2])
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+3] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+3])
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+4] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+4])
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+5] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+5])
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+6] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+6])
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+7] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+7])

            #             # Mode 0
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1]))
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1]))
            #             #  Mode 1
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+1] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+1]))
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+1] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+1]))
            #             #  Mode 2
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+2] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+2]))
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+2] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+2]))
            #             #  Mode 3
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+3] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+3]))
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+3] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+3]))
            #             #  Mode 4
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+4] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+4]))
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+4] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+4]))
            #             #  Mode 5
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+5] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+5]))
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+5] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+5]))
            #             #  Mode 6
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+6] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+6]))
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+6] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+6]))
            #             #  Mode 7
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+7] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+7]))
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+7] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+7]))

            #             #  Old contraints
            #             # Mode 0
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1] <= (P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1] - EPSILON)
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1] >= 0 * d_tilde_k[Global_Idx_1])

            #             # Mode 1
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+1] <= 2*(P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1+1] - EPSILON) 
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+1] >= (P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+1])

            #             # Mode 2
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+2] <= 3*(P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1+2] - EPSILON)
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+2] >= 2*(P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+2])

            #             # Mode 3
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+3] <= 4*(P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1+3])
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+3] >= 3*(P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+3])

            #             # Mode 4
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+4] <= 0 * d_tilde_k[Global_Idx_1+4] - EPSILON)
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+4] >= -(P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+4] + EPSILON)

            #             # Mode 5
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+5] <= -(P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1+5])
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+5] >= -2*(P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+5] + EPSILON)

            #             # Mode 6
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+6] <= -2*(P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1+6])
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+6] >= -3*(P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+6] + EPSILON)

            #             # Mode 7
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+7] <= -3*(P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1+7])
            #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+7] >= -4*(P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+7])

            #             Global_Idx_1 += 8
            #             Global_Idx_2 += 1

            # Cost function matrices
            H_Optimization = (np.transpose(C_Optimization) @ Q_Optimization @ C_Optimization) + R_Optimization
            # Hu_Optimization_PWA = (np.transpose(C_Optimization) @ Q_Optimization @ C_Optimization) + R_Optimization_PWA

            # Cost function for the minimization of the auxiliary variables
            # R_Optimization_z = np.zeros((8*number_of_agents_l*PREDICTION_HORIZON,8*number_of_agents_l*PREDICTION_HORIZON))
            # for Idx in range(0, len(R_Optimization_z)):
            #     R_Optimization_z[Idx,Idx] = 1

            # Hz_Optimization =  (np.transpose(Cz_Optimization) @ Q_Optimization @ Cz_Optimization) + R_Optimization_z

            # Cost function 
            # Stage cost including ADMM
            gamma_l = gamma[l].reshape(len(gamma[l]),).copy()
            consensus_variable_l = consensus_variable[l].reshape(len(consensus_variable[l]),).copy()
            avarage_variable_l = avarage_variable[l].reshape(len(avarage_variable[l]),).copy()
            
            # Stage_Cost = (u_tilde_k.T @ H_Optimization @ u_tilde_k) + 2*(np.transpose(x_k_l) @ np.transpose(M_Optimization) - reference_k_l.T) @ Q_Optimization @ C_Optimization @ u_tilde_k  + 2*(np.transpose(external_signals_k_l) @ np.transpose(D_Optimization)) @ Q_Optimization @ C_Optimization @ u_tilde_k + np.transpose(gamma_l)@(consensus_variable_l - avarage_variable_l) + (rho/2)*np.transpose(consensus_variable_l - avarage_variable_l)@(consensus_variable_l - avarage_variable_l)
            Stage_Cost = (u_tilde_k.T @ H_Optimization @ u_tilde_k) + 2*(np.transpose(x_k_l) @ np.transpose(M_Optimization) - reference_k_l.T) @ Q_Optimization @ C_Optimization @ u_tilde_k  + 2*(np.transpose(external_signals_k_l) @ np.transpose(D_Optimization)) @ Q_Optimization @ C_Optimization @ u_tilde_k 
            

            # Options
            gurobi_model.setObjective(Stage_Cost, gp.GRB.MINIMIZE) 
            gurobi_model.Params.LogToConsole = 0
            # gurobi_model.Params.FeasibilityTol = 1e-9
            # gurobi_model.Params.NumericFocus = 1
            
            # Local Optimization
            gurobi_model.optimize()

            # Results
            # Local variables
            u_local_k = np.zeros((NUM_INPUTS*number_of_agents_l, PREDICTION_HORIZON))
            PDisp_local_k = np.zeros((number_of_agents_l, PREDICTION_HORIZON))
            PESS_local_k = np.zeros((2*number_of_agents_l, PREDICTION_HORIZON))
            x_local_k = np.zeros((NUM_STATES*number_of_agents_l, PREDICTION_HORIZON+1))
            # z_local_k = np.zeros((8*number_of_agents_l, PREDICTION_HORIZON))
            d_local_k = np.zeros((2*number_of_agents_l,PREDICTION_HORIZON))

            var_idx = 0
            for j in range(0, PREDICTION_HORIZON):
                for i in range(0,NUM_INPUTS*number_of_agents_l):
                    u_local_k[i,j] = gurobi_model.getVars()[var_idx].x
                    var_idx += 1
            # var_idx = 0
            # for j in range(0, PREDICTION_HORIZON):
            #     for i in range(0,number_of_agents_l):
            #         PDisp_local_k[i,j] = gurobi_model.getVars()[var_idx].x
            #         var_idx += 1
            # for j in range(0, PREDICTION_HORIZON):
            #     for i in range(0,number_of_agents_l):
            #         PESS_local_k[i,j] = gurobi_model.getVars()[var_idx].x
            #         var_idx += 1
            # for j in range(0, PREDICTION_HORIZON):
            #     for i in range(0,8*number_of_agents_l):
            #         z_local_k[i,j] = gurobi_model.getVars()[var_idx].x
            #         var_idx += 1

            # Local initial state
            Global_Idx = 0
            for i in range(0,NUMBER_ATOMIC_AGENTS):
                if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
                    x_local_k[Global_Idx:Global_Idx+NUM_STATES,0] = x_evolution[i:i+NUM_STATES,k]
                    Global_Idx += NUM_STATES

            # THIS IS WRONG, NOT OVER THE PREDICTION HORIZON
            Global_Idx = 0
            for i in range(0, NUMBER_ATOMIC_AGENTS):
                if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
                    d_local_k[Global_Idx:Global_Idx +2,:] = np.array([MEASURED_LOAD_INCREMENTS[i,k:k+PREDICTION_HORIZON],
                                                                      MEASURED_RENEWABLE_INCREMENTS[i,k:k+PREDICTION_HORIZON]])
                    # DIFFERENCE BETWEENMEASURED AND FORECAST
                    # d_local_k[Global_Idx:Global_Idx +2,0] = np.array([MEASURED_LOAD_INCREMENTS[i,k],
                    #                                                   MEASURED_RENEWABLE_INCREMENTS[i,k]])
                    # d_local_k[Global_Idx:Global_Idx +2,1:1+PREDICTION_HORIZON] = np.array([MEASURED_LOAD_INCREMENTS[i,k+1:k+PREDICTION_HORIZON],
                    #                                                   MEASURED_RENEWABLE_INCREMENTS[i,k+1:k+PREDICTION_HORIZON]])
                    Global_Idx += 2

            # Local simualtion
            A_Augmented = Control_Agents_Matrices[l][0].copy()
            B_Augmented = Control_Agents_Matrices[l][1].copy()
            # Bz_Augmented = Control_Agents_Matrices[l][4].copy()
            D_Augmented = Control_Agents_Matrices[l][5].copy()

            for k_local in range(0,PREDICTION_HORIZON):
                x_local_k[:,k_local+1] = A_Augmented @ x_local_k[:,k_local] + B_Augmented @ u_local_k[:,k_local] + D_Augmented @ d_local_k[:,k_local]
                # x_local_k[:,k_local+1] = A_Augmented @ x_local_k[:,k_local] + B_Augmented @ u_local_k[:,k_local] + D_Augmented @ external_signals_k_l

            u_local[l] = u_local_k.copy()
            x_local[l] = x_local_k[:,1:].copy()

            # Build the consensus variable
            y_consensus = np.zeros((0,0))
            
            for i in range(0,NUM_INPUTS*number_of_agents_l):
                y_consensus = np.concatenate((y_consensus,u_local_k[i,:]), axis=None)
            for i in range(0,NUM_STATES*number_of_agents_l):
                y_consensus = np.concatenate((y_consensus,x_local_k[i,1:]), axis=None)

            consensus_variable[l] = y_consensus.T

            # Global input

            for i in range(0,NUMBER_ATOMIC_AGENTS):
                Agent_Index = LIST_ATOMIC_AGENTS[i]
                for j in range(0,len(Control_Agents[l])):
                    if Agent_Index == Control_Agents[l][j]:
                        Agent_Index_Augmented = Augmented_Control_Agents[l].index(Agent_Index)
                        # print("Agent: ", i)
                        # print("Selection: ", Augmented_Control_Agents[l][Agent_Index])
                        u_evolution[i*NUM_INPUTS:(i+1)*NUM_INPUTS,k] = u_local_k[Agent_Index_Augmented*NUM_INPUTS:(Agent_Index_Augmented+1)*NUM_INPUTS,0].copy()
            
            
            Total_Time_Holder = tm.time() - Start_Time_Holder
            Core_Seconds[k][l,number_of_iterations] = Core_Seconds[k][l,number_of_iterations] + Total_Time_Holder

        # MARK: Consensus Structure

        u_avarage_local = np.zeros((NUM_INPUTS*NUMBER_ATOMIC_AGENTS, PREDICTION_HORIZON))
        x_avarage_local = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS, PREDICTION_HORIZON))
        total_copies_vector = np.zeros((NUMBER_CONTROL_AGENTS))

        for l in range(0,NUMBER_ATOMIC_AGENTS):   
            
            total_copies = 0

            for i in range(0,NUMBER_CONTROL_AGENTS):
                Start_Time_Holder = tm.time()
                u_local_k = u_local[i]
                x_local_k = x_local[i]
                for j in range(0,len(Augmented_Control_Agents[i])):
                    if l == Augmented_Control_Agents[i][j]:
                        u_avarage_local[l*NUM_INPUTS:(l+1)*NUM_INPUTS,:] = u_avarage_local[l*NUM_INPUTS:(l+1)*NUM_INPUTS,:] + u_local_k[j*NUM_INPUTS:(j+1)*NUM_INPUTS,:]
                        x_avarage_local[l*NUM_STATES:(l+1)*NUM_STATES,:] = x_avarage_local[l*NUM_STATES:(l+1)*NUM_STATES,:] + x_local_k[j*NUM_STATES:(j+1)*NUM_STATES,:]
                        total_copies += 1
                Total_Time_Holder = tm.time() - Start_Time_Holder
                Core_Seconds[k][i,number_of_iterations] = Core_Seconds[k][i,number_of_iterations] + Total_Time_Holder
            if total_copies > 0:        
                u_avarage_local[l*NUM_INPUTS:(l+1)*NUM_INPUTS,:] = u_avarage_local[l*NUM_INPUTS:(l+1)*NUM_INPUTS,:]/total_copies
                x_avarage_local[l*NUM_STATES:(l+1)*NUM_STATES,:] = x_avarage_local[l*NUM_STATES:(l+1)*NUM_STATES,:]/total_copies
            

        # Computation of the avarage variable for each control agent
        for l in range(0,NUMBER_CONTROL_AGENTS):
            Start_Time_Holder = tm.time()

            number_of_agents_l = len(Augmented_Control_Agents[l])

            y_avarage = np.zeros((0,0))

            for i in range(0,number_of_agents_l):
                variable_index = LIST_ATOMIC_AGENTS.index(Augmented_Control_Agents[l][i])
                for Input_Index in range(0,NUM_INPUTS):
                    y_avarage = np.concatenate((y_avarage,u_avarage_local[(variable_index*NUM_INPUTS)+Input_Index,:]), axis=None)
            for i in range(0,number_of_agents_l):
                variable_index = LIST_ATOMIC_AGENTS.index(Augmented_Control_Agents[l][i])
                for Input_Index in range(0,NUM_STATES):
                    y_avarage = np.concatenate((y_avarage,x_avarage_local[(variable_index*NUM_STATES)+Input_Index,:]), axis=None)
            
            total_neighbors = 1
            if len(Augmented_Control_Agents[l]) - len(Control_Agents[l]) > 0:
                total_neighbors = len(Augmented_Control_Agents[l]) - len(Control_Agents[l])
            gamma_l = gamma[l].reshape(len(gamma[l]),).copy()
            avarage_variable[l] = y_avarage.T + ((1/(rho*total_neighbors))*gamma_l )
            Total_Time_Holder = tm.time() - Start_Time_Holder
            Core_Seconds[k][l,number_of_iterations] = Core_Seconds[k][l,number_of_iterations] + Total_Time_Holder
            


        #  Gamma Update
        for l in range(0,len(Augmented_Control_Agents)):
            Start_Time_Holder = tm.time()
            y_consensus = consensus_variable[l].reshape(len(consensus_variable[l]),).copy()
            y_avarage = avarage_variable[l].reshape(len(avarage_variable[l]),).copy()
            gamma_l = gamma[l].reshape(len(gamma[l]),).copy()
            gamma[l] = gamma_l + rho*(y_consensus - y_avarage)
            Total_Time_Holder = tm.time() - Start_Time_Holder
            Core_Seconds[k][l,number_of_iterations] = Core_Seconds[k][l,number_of_iterations] + Total_Time_Holder

        # Check norm conditions
        norm_codition_1 = True
        norm_codition_2 = True
        norm_codition_3 = True

        max_norm_error_1 = float('-inf')
        max_norm_error_2 = float('-inf')

        for l in range(0,NUMBER_CONTROL_AGENTS):
            Start_Time_Holder = tm.time()

            y_consensus = consensus_variable[l].copy()
            y_avarage = avarage_variable[l].copy()
            y_avarage_old = avarage_variable_old[l].copy()

            gamma_l = gamma[l].copy()
            alpha_l = np.linalg.norm(y_consensus - y_avarage, ord = 2)
            beta_l = rho*np.linalg.norm(y_avarage - y_avarage_old, ord = 2)

            epsilon_1 = 0.001*max(np.linalg.norm(y_consensus, ord = 2), np.linalg.norm(y_avarage, ord = 2))
            epsilon_2 = 0.001*np.linalg.norm(gamma_l, ord = 2)
            
            if alpha_l > epsilon_1:
                norm_codition_1 = False
            if alpha_l - epsilon_1> max_norm_error_1:
                max_norm_error_1 = alpha_l - epsilon_1
            
            if beta_l > epsilon_2:
                norm_codition_2 = False
            if beta_l - epsilon_2> max_norm_error_2:
                max_norm_error_2 = beta_l - epsilon_2
            Total_Time_Holder = tm.time() - Start_Time_Holder
            Core_Seconds[k][l,number_of_iterations] = Core_Seconds[k][l,number_of_iterations] + Total_Time_Holder

        for l in range(0,NUMBER_CONTROL_AGENTS):
            gamma_l = gamma[l].reshape(len(gamma[l]),).copy()
            consensus_variable_l = consensus_variable[l].reshape(len(consensus_variable[l]),).copy()
            avarage_variable_l = avarage_variable[l].reshape(len(avarage_variable[l]),).copy()
            residual_norm[l] = np.linalg.norm(consensus_variable_l - avarage_variable_l, ord=2)
            
        # norm_codition_1 = True
        for l in range(0,NUMBER_CONTROL_AGENTS):
            if residual_norm[l] > epsilon_convergence:
                norm_codition_3 = False

        # if (max_norm_error_1 < 0) and (max_norm_error_2 < 0):
        #     norm_codition_2 = True 


        residual_evolution[number_of_iterations] = residual_evolution[number_of_iterations] + np.max(residual_norm)
    
        #  Update number of iteration
        number_of_iterations += 1
        #  Print exit conditions
        if norm_codition_1 == True:
            print("---------------> Exit for norm condition 1. Max norm:", np.max(residual_norm))
        elif norm_codition_2 == True:
            print("---------------> Exit for norm condition 2. Max norm:", np.max(residual_norm))
        elif norm_codition_3 == True:
            print("---------------> Exit for norm condition 3. Max norm:", np.max(residual_norm))
        elif number_of_iterations >= max_number_of_iterations:
            print("---------------> Exit for max iterations", np.max(residual_norm))
        else:
            print("---------------> Reiteration. Max norm:", np.max(residual_norm))

        
        print("Max deviation condition 1: ", max_norm_error_1)
        print("Max deviation condition 2: ", max_norm_error_2)
        # #  Print exit conditions
        # if norm_codition_1 == True:
        #     print("---------------> Exit for norm condition 1. Max norm:", np.max(residual_norm))
        # elif norm_codition_2 == True:
        #     print("---------------> Exit for norm condition 2. Max norm:", np.max(residual_norm))
        # elif number_of_iterations >= max_number_of_iterations:
        #     print("---------------> Exit for max iterations")
        # else:
        #     print("---------------> Reiteration. Max norm:", np.max(residual_norm))
        
        # print("Max deviation condition 1: ", max_norm_error_1)
        # print("Max deviation condition 2: ", max_norm_error_2)
    
    # State update using PWA dynamics and global solution
    print("Mean evolution error norm = ", (np.linalg.norm(Reference_Signal[:,k] - x_evolution[:,k]))/NUMBER_ATOMIC_AGENTS)
    NUMBER_ATOMIC_AGENTS = PARAMETERS_LIST[0]
    UPPER_BOUNDS_STATE = PARAMETERS_LIST[8]
    TAU = PARAMETERS_LIST[13]

    A_Dynamics = PARAMETERS_LIST[3].copy()
    B_Dynamics = PARAMETERS_LIST[4].copy()
    D_Dynamics = PARAMETERS_LIST[5].copy()

    # B_Dynamics = B_Dynamics_Nominal.copy()


    # ETA_CHARGING_VALUES = np.array([[0.9],
    #                                 [0.7],
    #                                 [0.5],
    #                                 [0.3]])
    # ETA_DISCHARGING_VALUES = np.array([[1/0.9],
    #                                     [1/0.7],
    #                                     [1/0.5],
    #                                     [1/0.3]])

    # for i in range(0,NUMBER_ATOMIC_AGENTS):
        
    #     e_i_MAX = UPPER_BOUNDS_STATE[2,i]
    #     e_i_Percentage = (x_evolution[(i*NUM_STATES)+2,k]*100)/e_i_MAX 
    #     Eta = 0 
    #     if u_evolution[(i*2)+1,k] >= 0:
    #         if 0 <= e_i_Percentage < 25:
    #             Eta = ETA_CHARGING_VALUES[0,0]
    #         elif 25 <= e_i_Percentage < 50:
    #             Eta = ETA_CHARGING_VALUES[1,0]
    #         elif 50 <= e_i_Percentage < 75:
    #             Eta = ETA_CHARGING_VALUES[2,0]
    #         elif 75 <= e_i_Percentage <= 100:
    #             Eta = ETA_CHARGING_VALUES[3,0]

    #     elif u_evolution[(i*2)+1,k] < 0:
    #         if 0 <= e_i_Percentage < 25:
    #             Eta = ETA_DISCHARGING_VALUES[0,0]
    #         elif 25 <= e_i_Percentage < 50:
    #             Eta = ETA_DISCHARGING_VALUES[1,0]
    #         elif 50 <= e_i_Percentage < 75:
    #             Eta = ETA_DISCHARGING_VALUES[2,0]
    #         elif 75 <= e_i_Percentage <= 100:
    #             Eta = ETA_DISCHARGING_VALUES[3,0]

    #     B_Dynamics[(i*NUM_STATES)+2,(i*2)+1] = TAU*Eta

    # State update using PWA dynamics and global solution
    print("Mean evolution error norm = ", (np.linalg.norm(Reference_Signal[:,k] - x_evolution[:,k]))/NUMBER_ATOMIC_AGENTS)
    Simulation_Timer_End = tm.time() - Simulation_Timer_Start
    print("Enlapsed time:", round(Simulation_Timer_End,2), "[s]")
    print("Expected time to finish:", round(((Simulation_Timer_End*SIMULATION_HORIZON)/(k+1)) - Simulation_Timer_End, 2), "[s]")

    x_evolution[:,k+1] =  A_Dynamics @ x_evolution[:,k] + B_Dynamics @ u_evolution[:,k] + D_Dynamics @ w_evolution[:,k]
    # DIFFERENCE BETWEEN MEASURED AND FORECAST
    # w_evolution[:,k+1] = w_measured[:,k+1].copy()
Simulation_Total_Time = tm.time() - Simulation_Start_Time_Holder
print("Simulation = ", Simulation_Total_Time, " [s]")

# %% 
# MARK: Plots

if DRAW_PLOTS == True:
    Plot_State_01 = go.Figure(go.Scatter(x=np.arange(0,SIMULATION_HORIZON), y=x_evolution[0,:], name=f"D Delta_{LIST_ELECTRICAL_AREAS[0]}", mode='lines', line_shape='hv'))

    for q in range(1,NUMBER_ATOMIC_AGENTS):
        Plot_State_01.add_scatter(x=np.arange(0,SIMULATION_HORIZON), y=x_evolution[q*NUM_STATES,:], name=f"D Delta_{LIST_ELECTRICAL_AREAS[q]}", mode='lines', line_shape='hv')

    Plot_State_01.update_layout(title="Machine angle deviation", title_x=0.5, 
                    xaxis_title="Time step k", yaxis_title="D Delta(k)", template=plotly_template, width=800, height=500)  
    
    Plot_State_01.show()

    Plot_State_02 = go.Figure(go.Scatter(x=np.arange(0,SIMULATION_HORIZON), y=x_evolution[1,:], name=f"D f_{LIST_ELECTRICAL_AREAS[0]}", mode='lines', line_shape='hv'))

    for q in range(1,NUMBER_ATOMIC_AGENTS):
        Plot_State_02.add_scatter(x=np.arange(0,SIMULATION_HORIZON), y=x_evolution[(q*NUM_STATES)+1,:], name=f"D f_{LIST_ELECTRICAL_AREAS[q]}", mode='lines', line_shape='hv')

    Plot_State_02.update_layout(title="Frequency deviation", title_x=0.5, 
                    xaxis_title="Time step k", yaxis_title="D f(k)", template=plotly_template, width=800, height=500)  
    
    Plot_State_02.show()

    Plot_State_03 = go.Figure(go.Scatter(x=np.arange(0,SIMULATION_HORIZON), y=x_evolution[2,:], name=f"e_{LIST_ELECTRICAL_AREAS[0]}", mode='lines', line_shape='hv'))

    for q in range(1,NUMBER_ATOMIC_AGENTS):
        Plot_State_03.add_scatter(x=np.arange(0,SIMULATION_HORIZON), y=x_evolution[(q*NUM_STATES)+2,:], name=f"e_{LIST_ELECTRICAL_AREAS[q]}", mode='lines', line_shape='hv')

    Plot_State_03.update_layout(title="Stored energy", title_x=0.5, 
                    xaxis_title="Time step k", yaxis_title="e(k)", template=plotly_template, width=800, height=500)  
    
    Plot_State_03.show()

    ##### Input Pdisp

    Plot_Input_01 = go.Figure(go.Scatter(x=np.arange(0,SIMULATION_HORIZON), y=u_evolution[0,:], name=f"PDisp_{LIST_ELECTRICAL_AREAS[0]}", mode='lines', line_shape='hv'))

    for q in range(1,NUMBER_ATOMIC_AGENTS):
        Plot_Input_01.add_scatter(x=np.arange(0,SIMULATION_HORIZON), y=u_evolution[q*NUM_INPUTS,:], name=f"PDips_{LIST_ELECTRICAL_AREAS[q]}", mode='lines', line_shape='hv')

    Plot_Input_01.update_layout(title="Dispatchable generation", title_x=0.5, 
                    xaxis_title="Time step k", yaxis_title="Pdisp(k)", template=plotly_template, width=800, height=500)  
    
    Plot_Input_01.show()

    ##### Input PESS

    Plot_Input_02 = go.Figure(go.Scatter(x=np.arange(0,SIMULATION_HORIZON), y=u_evolution[1,:], name=f"PESS_{LIST_ELECTRICAL_AREAS[0]}", mode='lines', line_shape='hv'))

    for q in range(1,NUMBER_ATOMIC_AGENTS):
        Plot_Input_02.add_scatter(x=np.arange(0,SIMULATION_HORIZON), y=u_evolution[(q*NUM_INPUTS)+1,:], name=f"PESS_{LIST_ELECTRICAL_AREAS[q]}", mode='lines', line_shape='hv')

    Plot_Input_02.update_layout(title="ESS charging power", title_x=0.5, 
                    xaxis_title="Time step k", yaxis_title="PESS(k)", template=plotly_template, width=800, height=500)  
    
    
    Plot_Input_02.show()

    Plot_Input_03 = go.Figure(go.Scatter(x=np.arange(0,SIMULATION_HORIZON), y=u_evolution[2,:], name=f"PESS_{LIST_ELECTRICAL_AREAS[0]}", mode='lines', line_shape='hv'))

    for q in range(1,NUMBER_ATOMIC_AGENTS):
        Plot_Input_03.add_scatter(x=np.arange(0,SIMULATION_HORIZON), y=u_evolution[(q*NUM_INPUTS)+2,:], name=f"PESS_{LIST_ELECTRICAL_AREAS[q]}", mode='lines', line_shape='hv')

    Plot_Input_03.update_layout(title="ESS dicharging power", title_x=0.5, 
                    xaxis_title="Time step k", yaxis_title="PESS(k)", template=plotly_template, width=800, height=500)  
    
    
    Plot_Input_03.show()

    

# %%
# MARK: Cost function

Cost_Function = np.zeros((SIMULATION_HORIZON))
# print(Cost_Function.shape)
for k in range(0,SIMULATION_HORIZON):
    # print(x_evolution[:,k+1])
    # print(Reference_Signal[:,k+1])
    # print(u_evolution[:,k])
    # print(Cost_Function[k])
    if k > 0:
        Cost_Function[k] = Cost_Function[k-1] + ((x_evolution[:,k+1] - Reference_Signal[:,k+1]).T @ Q @ (x_evolution[:,k+1] - Reference_Signal[:,k+1])) + (u_evolution[:,k].T @ R @ u_evolution[:,k])
    else:
        Cost_Function[k] = ((x_evolution[:,k+1] - Reference_Signal[:,k+1]).T @ Q @ (x_evolution[:,k+1] - Reference_Signal[:,k+1])) + (u_evolution[:,k].T @ R @ u_evolution[:,k])

# %%
# MARK: Evaluation plots

Plot_Cost = go.Figure(go.Scatter(x=np.arange(0,SIMULATION_HORIZON), y=Cost_Function[:], name=f"PESS_{LIST_ELECTRICAL_AREAS[0]}", mode='lines', line_shape='hv'))


Plot_Cost.update_layout(title="Cost Function", title_x=0.5, 
                    xaxis_title="Time step k", yaxis_title="J(k)", template=plotly_template, width=800, height=500)  
    
    
Plot_Cost.show()

Plot_Residual= go.Figure(go.Scatter(x=np.arange(0,SIMULATION_HORIZON), y=residual_evolution[:], name=f"PESS_{LIST_ELECTRICAL_AREAS[0]}", mode='lines', line_shape='hv'))


Plot_Residual.update_layout(title="Residual Evolution", title_x=0.5, 
                    xaxis_title="Time step k", yaxis_title="r(k)", template=plotly_template, width=800, height=500)  
    
    
Plot_Residual.show()

# %%
# MARK: Evaluation metrics
# Total cost
print(Simulation_ID)
print("Number of control agents: ", NUMBER_CONTROL_AGENTS)
print("Total cost: ", Cost_Function[SIMULATION_HORIZON-1])

Total_Core_Seconds = 0
Total_Computation_Time = 0
Total_Number_ADMM_Iterations = 0
Max_Time_Iteration = 0
for k in range(0,SIMULATION_HORIZON):
    for i in range(0, max_number_of_iterations):
        Max_Time_Iteration = np.max(Core_Seconds[k][:,i],0)
        Total_Core_Seconds = Total_Core_Seconds + NUMBER_CONTROL_AGENTS*Max_Time_Iteration
        Total_Computation_Time = Total_Computation_Time + Max_Time_Iteration
        if Max_Time_Iteration > 0:
            Total_Number_ADMM_Iterations += 1

print("Total computation time: ", Total_Computation_Time)
print("Total core seconds: ", Total_Core_Seconds)
print("Total ADMM Iterations: ", Total_Number_ADMM_Iterations)

# %%
# MARK: Export Data
Simulation_Data = [[PARAMETERS_LIST],[MEASURED_LOAD],[MEASURED_RENEWABLE],[MEASURED_LOAD_INCREMENTS],[MEASURED_RENEWABLE_INCREMENTS],[INITIAL_DISPATCHABLE_POWER],[Control_Agents],[Augmented_Control_Agents],[Control_Agents_Matrices],[Control_Agents_Optimization_Matrices],[Weighted_Adjacency_Matrix],[Reference_Signal],[u_evolution],[x_evolution],[w_evolution],[Simulation_Total_Time],[Total_Computation_Time],[Total_Core_Seconds],[Total_Number_ADMM_Iterations],[Cost_Function],[residual_evolution]]

if EXPORT_DATA == True:
    with open(OUTPUT_FOLDER + "/" + Simulation_ID + "_SimulationData", 'wb') as Write_File:
        pk.dump(Simulation_Data, Write_File)

if (DRAW_PLOTS == True) and (EXPORT_PLOTS == True):
    Plot_State_01.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_State_01.pdf", width=1200, height=733, scale=3)
    Plot_State_02.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_State_02.pdf", width=1200, height=733, scale=3)
    Plot_State_03.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_State_03.pdf", width=1200, height=733, scale=3)
    Plot_Input_01.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Input_01.pdf", width=1200, height=733, scale=3)
    Plot_Input_02.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Input_02.pdf", width=1200, height=733, scale=3)
    Plot_Measured_Load.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Measured_Load.pdf", width=1200, height=733, scale=3)
    Plot_Measured_Renewable.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Measured_Renewable.pdf", width=1200, height=733, scale=3)
    Plot_Measured_Load_Increments.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Measured_Load_Increments.pdf", width=1200, height=733, scale=3)
    Plot_Measured_Renewable_Increments.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Measured_Renewable_Increments.pdf", width=1200, height=733, scale=3)
    Plot_Cost.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Cost.pdf", width=1200, height=733, scale=3)
    Plot_Residual.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Residual.pdf", width=1200, height=733, scale=3)

    Plot_State_01.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_State_01.jpeg", width=1200, height=733, scale=3)
    Plot_State_02.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_State_02.jpeg", width=1200, height=733, scale=3)
    Plot_State_03.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_State_03.jpeg", width=1200, height=733, scale=3)
    Plot_Input_01.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Input_01.jpeg", width=1200, height=733, scale=3)
    Plot_Input_02.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Input_02.jpeg", width=1200, height=733, scale=3)
    Plot_Measured_Load.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Measured_Load.jpeg", width=1200, height=733, scale=3)
    Plot_Measured_Renewable.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Measured_Renewable.jpeg", width=1200, height=733, scale=3)
    Plot_Measured_Load_Increments.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Measured_Load_Increments.jpeg", width=1200, height=733, scale=3)
    Plot_Measured_Renewable_Increments.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Measured_Renewable_Increments.jpeg", width=1200, height=733, scale=3)
    Plot_Cost.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Cost.jpeg", width=1200, height=733, scale=3)
    Plot_Residual.write_image(OUTPUT_FOLDER + "/" + Simulation_ID + "_Plot_Residual.jpeg", width=1200, height=733, scale=3)