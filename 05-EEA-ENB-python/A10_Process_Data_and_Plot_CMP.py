# %% 
# MARK: Reset Operations

from IPython import get_ipython
get_ipython().run_line_magic('reset', '-f')
# print("\n" * 100)

#  %%
# MARK: Options

EXPORT_DATA = True
DRAW_PLOTS = True
EXPORT_PLOTS = True

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
# plotly_template = "plotly_white"
plotly_template = "plotly_dark"

# random numbers
import random as rnd
# rnd.seed(1)

# For time tracking
import time as tm

# Support functions
from A00_Support_Functions import * 

# %%
Simulation_ID = "18_EAA_CMPC_ESS_CHARGE_SimulationData"
FILE_NAME = OUTPUT_FOLDER + "/" + Simulation_ID

with open(FILE_NAME, 'rb') as file:
    Simulation_Data = pk.load(file)

# %%
 # MARK: For centralized MPC
PARAMETERS_LIST = Simulation_Data[0][0]
NUMBER_ATOMIC_AGENTS = PARAMETERS_LIST[0]
SIMULATION_HORIZON = PARAMETERS_LIST[1]
Eta = Simulation_Data[1][0]
MEASURED_LOAD = Simulation_Data[2][0]
MEASURED_RENEWABLE = Simulation_Data[3][0]
MEASURED_LOAD_INCREMENTS = Simulation_Data[4][0]
MEASURED_RENEWABLE_INCREMENTS = Simulation_Data[5][0]
INITIAL_DISPATCHABLE_POWER = Simulation_Data[6][0]
Control_Agents = Simulation_Data[7][0]
Augmented_Control_Agents = Simulation_Data[8][0]
Control_Agents_Matrices = Simulation_Data[9][0]
Control_Agents_Optimization_Matrices = Simulation_Data[10][0]
Weighted_Adjacency_Matrix = Simulation_Data[11][0]
Reference_Signal = Simulation_Data[12][0]
u_evolution = Simulation_Data[13][0]
x_evolution = Simulation_Data[14][0]
w_evolution = Simulation_Data[15][0]
z_evolution = Simulation_Data[16][0]
d_evolution = Simulation_Data[17][0]
Simulation_Total_Time = Simulation_Data[18][0]


# %%
# MARK: Plot data
plt.rc('font', family='Times New Roman', size=18)  
plt.rc('text', usetex=True)
plt.tight_layout()

###################################################################### Load increments
Fig_Load, Ax_Load = plt.subplots(figsize=(9, 6), dpi=100)

Ax_Load.margins(x=0, y=None)
Ax_Load.grid(True, color='gray', alpha=0.2)

Ax_Load.set_title('Load increments', fontsize=26)
Ax_Load.set_xlabel('Time step')
Ax_Load.set_ylabel('GW')

for i in range(0,NUMBER_ATOMIC_AGENTS):
    Area_Index = Control_Agents[0][i]
    Ax_Load.step(range(0,SIMULATION_HORIZON), 
                    MEASURED_LOAD_INCREMENTS[i,0:SIMULATION_HORIZON], 
                    where='pre', 
                    label=fr'$\Delta P^{{Load}}_{{{Area_Index}}}$')
    plt.legend(loc='upper right', bbox_to_anchor=(1.27, 1.025))

###################################################################### Renewable generation increments
Fig_Ren, Ax_Ren = plt.subplots(figsize=(9, 6), dpi=100)

Ax_Ren.margins(x=0, y=None)
Ax_Ren.grid(True, color='gray', alpha=0.2)

Ax_Ren.set_title('Renewable generation increments', fontsize=26)
Ax_Ren.set_xlabel('Time step')
Ax_Ren.set_ylabel('GW')

for i in range(0,NUMBER_ATOMIC_AGENTS):
    Area_Index = Control_Agents[0][i]
    Ax_Ren.step(range(0,SIMULATION_HORIZON), 
                    MEASURED_RENEWABLE_INCREMENTS[i,0:SIMULATION_HORIZON], 
                    where='pre', 
                    label=fr'$\Delta P^{{Ren}}_{{{Area_Index}}}$')
    plt.legend(loc='upper right', bbox_to_anchor=(1.27, 1.025))

###################################################################### Input 1
Fig_Input_01, Ax_Input_01 = plt.subplots(figsize=(9, 6), dpi=100)

Ax_Input_01.margins(x=0, y=None)
Ax_Input_01.grid(True, color='gray', alpha=0.2)

Ax_Input_01.set_title('Dispatchable power variationn', fontsize=26)
Ax_Input_01.set_xlabel('Time step')
Ax_Input_01.set_ylabel('GW')

for i in range(0,NUMBER_ATOMIC_AGENTS):
    Area_Index = Control_Agents[0][i]
    Ax_Input_01.step(range(0,SIMULATION_HORIZON), 
                    u_evolution[i*2,0:SIMULATION_HORIZON], 
                    where='pre', 
                    label=fr'$\Delta P^{{Disp}}_{{{Area_Index}}}$')
    plt.legend(loc='upper right', bbox_to_anchor=(1.27, 1.025))

###################################################################### Input 1
Fig_Input_02, Ax_Input_02 = plt.subplots(figsize=(9, 6), dpi=100)

Ax_Input_02.margins(x=0, y=None)
Ax_Input_02.grid(True, color='gray', alpha=0.2)

Ax_Input_02.set_title('Power exschange with the ESS variation', fontsize=26)
Ax_Input_02.set_xlabel('Time step')
Ax_Input_02.set_ylabel('GW')

for i in range(0,NUMBER_ATOMIC_AGENTS):
    Area_Index = Control_Agents[0][i]
    Ax_Input_02.step(range(0,SIMULATION_HORIZON), 
                    u_evolution[(i*2+1),0:SIMULATION_HORIZON], 
                    where='pre', 
                    label=fr'$\Delta P^{{ESS}}_{{{Area_Index}}}$')
    plt.legend(loc='upper right', bbox_to_anchor=(1.27, 1.025))

###################################################################### State 1
Fig_State_01, Ax_State_01 = plt.subplots(figsize=(9, 6), dpi=100)

Ax_State_01.margins(x=0, y=None)
Ax_State_01.grid(True, color='gray', alpha=0.2)

Ax_State_01.set_title('Machine angle deviation', fontsize=26)
Ax_State_01.set_xlabel('Time step')
Ax_State_01.set_ylabel('Deg')

for i in range(0,NUMBER_ATOMIC_AGENTS):
    Area_Index = Control_Agents[0][i]
    Ax_State_01.step(range(0,SIMULATION_HORIZON), 
                    x_evolution[i*5,0:SIMULATION_HORIZON], 
                    where='pre', 
                    label=fr'$\Delta \delta_{{{Area_Index}}}$')
    plt.legend(loc='upper right', bbox_to_anchor=(1.23, 1.025))

###################################################################### State 2
Fig_State_02, Ax_State_02 = plt.subplots(figsize=(9, 6), dpi=100)

Ax_State_02.margins(x=0, y=None)
Ax_State_02.grid(True, color='gray', alpha=0.2)

Ax_State_02.set_title('Frequency deviation', fontsize=26)
Ax_State_02.set_xlabel('Time step')
Ax_State_02.set_ylabel('Hz')

for i in range(0,NUMBER_ATOMIC_AGENTS):
    Area_Index = Control_Agents[0][i]
    Ax_State_02.step(range(0,SIMULATION_HORIZON), 
                    x_evolution[(i*5)+1,0:SIMULATION_HORIZON], 
                    where='pre', 
                    label=fr'$\Delta f_{{{Area_Index}}}$')
    plt.legend(loc='upper right', bbox_to_anchor=(1.23, 1.025))

###################################################################### State 3
Fig_State_03, Ax_State_03 = plt.subplots(figsize=(9, 6), dpi=100)

Ax_State_03.margins(x=0, y=None)
Ax_State_03.grid(True, color='gray', alpha=0.2)

Ax_State_03.set_title('Energy stored in the ESS', fontsize=26)
Ax_State_03.set_xlabel('Time step')
Ax_State_03.set_ylabel('GW')

for i in range(0,NUMBER_ATOMIC_AGENTS):
    Area_Index = Control_Agents[0][i]
    Ax_State_03.step(range(0,SIMULATION_HORIZON), 
                    x_evolution[(i*5)+2,0:SIMULATION_HORIZON], 
                    where='pre', 
                    label=fr'$e_{{{Area_Index}}}$')
    plt.legend(loc='upper right', bbox_to_anchor=(1.23, 1.025))

###################################################################### State 4
Fig_State_04, Ax_State_04 = plt.subplots(figsize=(9, 6), dpi=100)

Ax_State_04.margins(x=0, y=None)
Ax_State_04.grid(True, color='gray', alpha=0.2)

Ax_State_04.set_title('Power transmitted over the tie-lines', fontsize=26)
Ax_State_04.set_xlabel('Time step')
Ax_State_04.set_ylabel('GW')

for i in range(0,NUMBER_ATOMIC_AGENTS):
    Area_Index = Control_Agents[0][i]
    Ax_State_04.step(range(0,SIMULATION_HORIZON), 
                    x_evolution[(i*5)+3,0:SIMULATION_HORIZON], 
                    where='pre', 
                    label=fr'$P^{{Tie}}_{{{Area_Index}}}$')
    plt.legend(loc='upper right', bbox_to_anchor=(1.23, 1.025))

###################################################################### State 5
Fig_State_05, Ax_State_05 = plt.subplots(figsize=(9, 6), dpi=100)

Ax_State_05.margins(x=0, y=None)
Ax_State_05.grid(True, color='gray', alpha=0.2)

Ax_State_05.set_title('Total dispatchable power', fontsize=26)
Ax_State_05.set_xlabel('Time step')
Ax_State_05.set_ylabel('GW')

for i in range(0,NUMBER_ATOMIC_AGENTS):
    Area_Index = Control_Agents[0][i]
    Ax_State_05.step(range(0,SIMULATION_HORIZON), 
                    x_evolution[(i*5)+4,0:SIMULATION_HORIZON], 
                    where='pre', 
                    label=fr'$P^{{Disp}}_{{{Area_Index}}}$')
    plt.legend(loc='upper right', bbox_to_anchor=(1.23, 1.025))

# %%
# MARK: Export plots

Fig_Load.savefig(OUTPUT_FOLDER + "/" + Simulation_ID + "_Fig_Load.pdf", format="pdf", dpi=300, bbox_inches='tight')
Fig_Ren.savefig(OUTPUT_FOLDER + "/" + Simulation_ID + "_Fig_Ren.pdf", format="pdf", dpi=300, bbox_inches='tight')

Fig_Input_01.savefig(OUTPUT_FOLDER + "/" + Simulation_ID + "_Fig_Inputs_01.pdf", format="pdf", dpi=300, bbox_inches='tight')
Fig_Input_02.savefig(OUTPUT_FOLDER + "/" + Simulation_ID + "_Fig_Inputs_02.pdf", format="pdf", dpi=300, bbox_inches='tight')

Fig_State_01.savefig(OUTPUT_FOLDER + "/" + Simulation_ID + "_Fig_State_01.pdf", format="pdf", dpi=300, bbox_inches='tight')
Fig_State_02.savefig(OUTPUT_FOLDER + "/" + Simulation_ID + "_Fig_State_02.pdf", format="pdf", dpi=300, bbox_inches='tight')
Fig_State_03.savefig(OUTPUT_FOLDER + "/" + Simulation_ID + "_Fig_State_03.pdf", format="pdf", dpi=300, bbox_inches='tight')
Fig_State_04.savefig(OUTPUT_FOLDER + "/" + Simulation_ID + "_Fig_State_04.pdf", format="pdf", dpi=300, bbox_inches='tight')
Fig_State_05.savefig(OUTPUT_FOLDER + "/" + Simulation_ID + "_Fig_State_05.pdf", format="pdf", dpi=300, bbox_inches='tight')


