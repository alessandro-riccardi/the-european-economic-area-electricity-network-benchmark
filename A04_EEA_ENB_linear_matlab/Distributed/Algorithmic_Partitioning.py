# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 7:49:47 2023

@author: ariccardi
"""


# %% Preliminary Operations

# %%% Clear Workspace

from IPython import get_ipython
get_ipython().run_line_magic('reset', '-sf')



# %%% Load Libraries

# For optimization
import gurobipy as gp
from gurobipy import GRB

# For linear algebra
import numpy as np
import scipy as sp

# For plots
import matplotlib.pyplot as plt

# For graphs plots
import networkx as nx

# For random numbers
import random as rn

# For results reproducibility
rn.seed(0)

# Math module
import math as mt

# For color Bar of Graphs
from matplotlib.colors import LinearSegmentedColormap, to_rgba 
from matplotlib.cm import ScalarMappable

# To stoep execution when testing
from sys import exit
import sys
sys.path.append("C/Users/ariccardi/Desktop/PhD/Code/Partitioning/Algorithmic")

# %%% Load Local Custom Modules

#  Random Network Generation
from Random_Network_Generation import *

# Lists Manipulation
from Elementary_Support_Functions import *
     
 
# %%% State Dynamics Generation

# Define the number of states and inputs
number_of_states = 12
number_of_inputs = 4 
# number_of_states = 50
# number_of_inputs = 10 
number_of_elemnts_per_column = 1
 
A, B = random_network_generator(number_of_states, number_of_inputs, number_of_elemnts_per_column)
             
# %% Identification of Atomic Control Agents
# %%% Initialization of empty lists and graphs

# Arrays of input and state nodes
Input_Nodes = np.arange(1,number_of_inputs+1)
State_Nodes = np.arange(number_of_inputs+1,number_of_inputs+number_of_states+1)


# List of the agents
Atomic_Agents = init_list_of_objects(number_of_inputs)
# List of the trees associated with the agents during their creation
Atomic_Agents_Trees = init_list_of_objects(number_of_inputs)
# List of the sub-graphs associated with the agents
Atomic_Agents_Graphs = init_list_of_objects(number_of_inputs)
# Create empty list of atomic agents matrices
Atomic_Agents_Matrices = init_list_of_objects(number_of_inputs)

# Initialization of Atomic Agents Graphs
for i in range(0,len(Atomic_Agents_Graphs)):
    Atomic_Agents_Trees[i] = nx.Graph()
    Atomic_Agents_Graphs[i] = nx.Graph()


# List of the nodes that still have to be assigned
Unassigned_Nodes = []
for i in range(1,number_of_inputs+number_of_states+1):
    Unassigned_Nodes.append(i)


# Graph of the entire network
G_complete = nx.Graph()

# Creation of the network graph
for i in range(0,number_of_inputs):
    G_complete.add_node(Input_Nodes[i])
    
for i in range(0,number_of_states):
    G_complete.add_node(State_Nodes[i])
    
for j in range(0,number_of_inputs):
    for i in range(0,number_of_states):
        if B[i,j] != 0:
            G_complete.add_edge(Input_Nodes[j], State_Nodes[i], weight=B[i,j])   

for i in range(0,number_of_states):
    for j in range(0,number_of_states):
        if A[i,j] != 0:
            G_complete.add_edge(State_Nodes[j], State_Nodes[i], weight=A[i,j]) 


# %%% Identifications of the Roots of Atomic Control Agents

for i in range(0,number_of_inputs):
    
    for j in range(0,number_of_states):
        
        if B[j,i] != 0:
            
            if check_2d(Atomic_Agents, Input_Nodes[i]) == False:    
                
                # New Atomic Agent one input node and one state node           
                if check_2d(Atomic_Agents, State_Nodes[j]) == False:
                    
                    Atomic_Agents[i].append(Input_Nodes[i])
                    Atomic_Agents[i].append(State_Nodes[j]) 
                                  
                    Unassigned_Nodes.remove(Input_Nodes[i])
                    Unassigned_Nodes.remove(State_Nodes[j])
                
                # Merge Atomic Agents through a couplig with a state ndoe  
                elif check_2d(Atomic_Agents, State_Nodes[j]) == True:
                    
                    idx_agent = index_2d(Atomic_Agents, State_Nodes[j])
                    
                    Atomic_Agents[idx_agent[0]].append(Input_Nodes[i])
                       
                    Unassigned_Nodes.remove(Input_Nodes[i])
            
            elif check_2d(Atomic_Agents, Input_Nodes[i]) == True:     
                
                # Add State Nodes To existing Agent
                if check_2d(Atomic_Agents, State_Nodes[j]) == False:
                    
                    idx_agent = index_2d(Atomic_Agents, Input_Nodes[i])
                    
                    Atomic_Agents[idx_agent[0]].append(State_Nodes[j])
                    
                    Unassigned_Nodes.remove(State_Nodes[j])


# %%% Sort Agents and remove empty agents

# Sort
Atomic_Agents.sort()
for k in range(0, len(Atomic_Agents)):
    Atomic_Agents[k].sort()

# Remove Empty Agents
while [] in Atomic_Agents:
    Atomic_Agents.remove([])


# %%% Update Atomic Agents Trees and Graphs

for k in range(0, len(Atomic_Agents)):
    
    for i in Atomic_Agents[k]:
        
        Atomic_Agents_Trees[k].add_node(i)
        Atomic_Agents_Graphs[k].add_node(i)
        
        if i in Input_Nodes: 
            
            for j in Atomic_Agents[k]:
                
                if j in State_Nodes:                
                    
                    if B[j-number_of_inputs-1,i-1] != 0:
                        
                        Atomic_Agents_Trees[k].add_edge(i, j, weight=B[j-number_of_inputs-1,i-1])
                        Atomic_Agents_Graphs[k].add_edge(i, j, weight=B[j-number_of_inputs-1,i-1])   
            

# %%% Assignments of the leafs of atomic control agents through forward exploration

reiterate = True

while reiterate == True:
    
    reiterate = False
    
    for i in range(0, number_of_states):
        
        if State_Nodes[i] in Unassigned_Nodes:
            
            A_max = 0
            j_max = 0
            
            for k in range(0,len(Atomic_Agents)):
                for j in range(0, number_of_states):    
                    if State_Nodes[j] in Atomic_Agents[k]:
                        if A[i,j] > A_max:
                            A_max = A[i,j]
                            j_max = j
            
            if A_max != 0:
                    
                idx_agent = index_2d(Atomic_Agents, State_Nodes[j_max])
                k = idx_agent[0]
                
                Atomic_Agents[k].append(State_Nodes[i])
                
                Unassigned_Nodes.remove(State_Nodes[i])
                
                reiterate = True

            
# %%% Assignments of the unassignad nodes 

i = 0
reiterate = False

while len(Unassigned_Nodes) > 0:
    
    reiterate = False
    
    if State_Nodes[i] in Unassigned_Nodes:
        
        j = np.argmax(A[:,i])
        
        if check_2d(Atomic_Agents, State_Nodes[j]) == True and np.max(A[:,i]) != 0:
            
            idx_agent = index_2d(Atomic_Agents, State_Nodes[j])
            k = idx_agent[0]
            
            Atomic_Agents[k].append(State_Nodes[i])    
                        
            Atomic_Agents_Graphs[k].add_node(State_Nodes[i]) 
            Atomic_Agents_Graphs[k].add_edge(State_Nodes[i], State_Nodes[j], weight=A[j,i])            
            
            Atomic_Agents_Trees[k].add_node(State_Nodes[i]) 
            Atomic_Agents_Trees[k].add_edge(State_Nodes[i], State_Nodes[j], weight=A[j,i])

            Unassigned_Nodes.remove(State_Nodes[i])
            
            reiterate = True     
            
    i += 1
    if i == number_of_states:
        break
    if reiterate == True:
        i = 0


# %%% Assignment of the edges to the Atomic Agents Graphs

for k in range(0, len(Atomic_Agents)):
    
    for i in range(0, number_of_states):
        
        if State_Nodes[i] in Atomic_Agents[k]:
        
            for j in range(0, number_of_inputs):
                
                if Input_Nodes[j] in Atomic_Agents[k]:
                    
                    if B[i,j] != 0:
                    
                        Atomic_Agents_Graphs[k].add_edge(Input_Nodes[j], State_Nodes[i], weight=B[i,j])
                        
        
            for j in range(0, number_of_states):
                
                if State_Nodes[j] in Atomic_Agents[k]:
                    
                    if A[i,j] != 0:
                        
                        Atomic_Agents_Graphs[k].add_edge(State_Nodes[j], State_Nodes[i], weight=A[i,j])

    
# %%% Build Atomic Control Agents state and input matrices

for k in range(0, len(Atomic_Agents)):
    
    # Detect the number of states and inputs
    nxi = 0
    nui = 0
        
    for i in range(0, len(Atomic_Agents[k])):
            
        if Atomic_Agents[k][i] <= number_of_inputs:              
            nui = nui + 1 
                
        elif Atomic_Agents[k][i] > number_of_inputs:          
            nxi = nxi + 1 
                
    Ai = np.full((nxi,nxi), 0, dtype='float64')
    Aij = np.full((nxi,number_of_states), 0, dtype='float64')
    Bi = np.full((nxi,nui), 0, dtype='float64')
        
    raw_xi = 0  
    col_ui = 0

    for i in Atomic_Agents[k]:
 
        if i > number_of_inputs:
            
            coli = 0
            
            for j in range(0, number_of_states):     
                    
                if State_Nodes[j] in Atomic_Agents[k]:

                    Ai[raw_xi,coli] = A[i-number_of_inputs-1,j]

                    coli = coli+1
                            
                if State_Nodes[j] not in Atomic_Agents[k]:
                    
                    if A[i-number_of_inputs-1,j] != 0:
                        
                        Aij[raw_xi,j] = A[i-number_of_inputs-1,j] 
                            
            raw_xi = raw_xi + 1
                
        elif i <= number_of_inputs:    
            
            raw_ui = 0   

            for j in range(0, number_of_states):
                    
                if State_Nodes[j] in Atomic_Agents[k]:

                    Bi[raw_ui,col_ui] = B[j,i-1]                       
                        
                    raw_ui = raw_ui + 1
                    
            col_ui = col_ui + 1    
                
    Atomic_Agents_Matrices[k] = [[Ai],[Bi],[Aij]]
        

# Remove Empty Agents' Matrices
while [] in Atomic_Agents_Matrices:
    Atomic_Agents_Matrices.remove([])

# %% Plot Network Graph 
# %%% Construction of the graphical graph

positions_G_Complete = init_list_of_objects(number_of_states + number_of_inputs)
degree_list = init_list_of_objects(number_of_states + number_of_inputs)

degree_list_raw = list(G_complete.degree())

# Determination of themaximum  radius of the network
for k in range(0, len(degree_list)):
    degree_list[k] = degree_list_raw[k][1]

max_radius = np.amax(degree_list)


# Basic radius for the node of the network
radius_circle = 0.15

# Positon index 
idx = 0

# Assignment of the positions of the nodes for input nodes
for i in range(0, number_of_inputs):
        
    positions_G_Complete[idx] = [Input_Nodes[i], max_radius * mt.cos((2*mt.pi*i)/(number_of_inputs)),
                                                 max_radius * mt.sin((2*mt.pi*i)/(number_of_inputs))]
        
    idx += 1


states_pos_indx = np.full(np.amax(degree_list) + 1, 0, dtype='float64')

# Assignment of the positions of the nodes for state nodes
for i in range(0, number_of_states):
    
    node_degree = degree_list[i + number_of_inputs]
    
    
    number_of_sections = degree_list.count(node_degree)
    
    positions_G_Complete[idx] = [State_Nodes[i], (max_radius + 1 - node_degree) * mt.cos((2*mt.pi*states_pos_indx[node_degree])/(number_of_sections)),
                                                 (max_radius + 1 - node_degree) * mt.sin((2*mt.pi*states_pos_indx[node_degree])/(number_of_sections))]
        
    states_pos_indx[node_degree] += 1    
    idx += 1


# %%% Plot Network Graph

plot_network_map = True
save_network_map = True

if plot_network_map == True:

    plt.figure(figsize=(50, 50), dpi=100)
    
    
    # Plot Arrows
    sin_val_A = np.linalg.svd(A)
    max_sin_val_A = np.amax(sin_val_A[1])
    
    sin_val_B = np.linalg.svd(B)
    max_sin_val_B = np.amax(sin_val_B[1])
    
    for i in range(0, number_of_states):
        for j in range(0, number_of_inputs):
            if B[i,j] != 0:
                
                x  = positions_G_Complete[j][1]
                y  = positions_G_Complete[j][2]
                dx = positions_G_Complete[i + number_of_inputs][1] - positions_G_Complete[j][1]
                dy = positions_G_Complete[i + number_of_inputs][2] - positions_G_Complete[j][2]
                
                
                angle = mt.atan2(dy,dx)
                x_shift = radius_circle*mt.cos(angle)
                y_shift = radius_circle*mt.sin(angle)
                
                plt.arrow(x, y, dx-x_shift, dy-y_shift, width=0.04, length_includes_head=True, color="cyan", alpha=abs(B[i,j])/max_sin_val_B)
    
    for i in range(0, number_of_states):
        for j in range(0, number_of_states):
            if A[i,j] != 0 and i != j:
                
                x  = positions_G_Complete[j + number_of_inputs][1]
                y  = positions_G_Complete[j + number_of_inputs][2]
                dx = positions_G_Complete[i + number_of_inputs][1] - positions_G_Complete[j + number_of_inputs][1]
                dy = positions_G_Complete[i + number_of_inputs][2] - positions_G_Complete[j + number_of_inputs][2]
                
                
                angle = mt.atan2(dy,dx)
                x_shift = radius_circle*mt.cos(angle)
                y_shift = radius_circle*mt.sin(angle)
                
                plt.arrow(x, y, dx-x_shift, dy-y_shift, width=0.04, length_includes_head=True, color="cyan", alpha=abs(A[i,j])/max_sin_val_A)
    
    
    # Plot Nodes
    ax = plt.gca()
    
    for k in range(0, len(positions_G_Complete)):
        
        if k < number_of_inputs:
            
            circle = plt.Circle((positions_G_Complete[k][1], positions_G_Complete[k][2]), radius_circle, color='black', alpha=1)
            ax.add_patch(circle)
            circle = plt.Circle((positions_G_Complete[k][1], positions_G_Complete[k][2]), radius_circle*0.9, color='r', alpha=1)
            ax.add_patch(circle)
            
            plt.text(positions_G_Complete[k][1], positions_G_Complete[k][2], str(positions_G_Complete[k][0]), color="black", fontsize=24, horizontalalignment="center", verticalalignment="center")
    
        else:
            circle = plt.Circle((positions_G_Complete[k][1], positions_G_Complete[k][2]), radius_circle, color='black', alpha=1)
            ax.add_patch(circle)
            circle = plt.Circle((positions_G_Complete[k][1], positions_G_Complete[k][2]), radius_circle*0.9, color='b', alpha=1)
            ax.add_patch(circle)
            
            plt.text(positions_G_Complete[k][1], positions_G_Complete[k][2], str(positions_G_Complete[k][0]), color="black", fontsize=24, horizontalalignment="center", verticalalignment="center")
    
    
    # Color Bar
    plot_color_map = False
    
    if plot_color_map == True:
        my_cmap = LinearSegmentedColormap.from_list(None, [(0, 1, 1, 0.0), (0, 0, 255, 100.0)])
        cbar = plt.colorbar(ScalarMappable(cmap=my_cmap), ticks=[0, 1], pad=0.02)
        cbar.ax.set_yticklabels(["Min", "Max"], fontsize=100)
    
    plt.tight_layout()
    
        
    plt.axis("equal")
    plt.axis('off') 
   
    fig = plt.gcf()   
    plt.show() 
    if save_network_map == True:
        fig.savefig("network_map.pdf", transparent=True, dpi='figure')
        
      
# %%% Position of nodes

# List of the positions of the nodes
positions = init_list_of_objects(number_of_states + number_of_inputs)

# %%% Determination of the number of rings of the circular graph

# Number of sections of the external radius
number_of_external_elements = len(Atomic_Agents) 

pos_idx = 0

# Basic radius unit used throughout the networks
radius = 1

rad_idx = 0
longest_path = 0

# Determination of the number of rings of the circular graph
for k in range(0,len(Atomic_Agents)): 
    
    for j in range(0, len(Atomic_Agents[k])):

        if Atomic_Agents[k][j] in State_Nodes:

            shortest_lenght = len(nx.shortest_path(Atomic_Agents_Graphs[k], source=Atomic_Agents[k][0], target=Atomic_Agents[k][j], weight=1))
    
            if shortest_lenght > longest_path:
                
                longest_path = shortest_lenght


# %%% Assignment of the Position of nodes
                    
for k in range(0,len(Atomic_Agents)): 
    
    # input nodes
    
    if Atomic_Agents[k] != []:

        n_ui = 0
        
        for j in range(0, len(Atomic_Agents[k])):
            
            if Atomic_Agents[k][j] in Input_Nodes:
                
                n_ui += 1
        
        
        k_ui = 1       
        
        for j in range(0, len(Atomic_Agents[k])):
            
            # index internal division
            if Atomic_Agents[k][j] in Input_Nodes:
                
                positions[pos_idx] = [Atomic_Agents[k][j],  (longest_path)*radius * mt.cos(((2 * mt.pi * rad_idx)/(number_of_external_elements)) + (((2*mt.pi)/(number_of_external_elements))/(n_ui+1))*k_ui), (longest_path)*radius * mt.sin(((2 * mt.pi * rad_idx)/(number_of_external_elements)) + (((2*mt.pi)/(number_of_external_elements))/(n_ui+1))*k_ui)]
                
                k_ui += 1 
                
                pos_idx += 1
                
        
        # State Nodes
        n_xi = 0
        
        max_eccentricity_tree = 0
        
        for j in range(0, len(Atomic_Agents[k])):
            
            if Atomic_Agents[k][j] in State_Nodes:

                if max_eccentricity_tree < len(nx.shortest_path(Atomic_Agents_Graphs[k], source=Atomic_Agents[k][0], target=Atomic_Agents[k][j],weight=1)):
                    
                    max_eccentricity_tree = len(nx.shortest_path(Atomic_Agents_Graphs[k], source=Atomic_Agents[k][0], target=Atomic_Agents[k][j],weight=1))  

                
        number_states_eccentricity = np.full(max_eccentricity_tree, 0, dtype='float64')
 
        for j in range(0, len(Atomic_Agents[k])):
            
            if Atomic_Agents[k][j] in State_Nodes:
                
                shortest_lenght = len(nx.shortest_path(Atomic_Agents_Graphs[k], source=Atomic_Agents[k][0], target=Atomic_Agents[k][j], weight=1))

                for l in range(0, len(Atomic_Agents[k])):
                    
                    if Atomic_Agents[k][l] in Input_Nodes:
                        
                        if len(nx.shortest_path(Atomic_Agents_Graphs[k], Atomic_Agents[k][l], Atomic_Agents[k][j])) < shortest_lenght:
                            
                            shortest_lenght = len(nx.shortest_path(Atomic_Agents_Graphs[k], Atomic_Agents[k][l], Atomic_Agents[k][j]))    
                
                
                eccentricity_state = shortest_lenght

                number_states_eccentricity[eccentricity_state-1] = number_states_eccentricity[eccentricity_state-1] + 1
                
        
        for m in range(0, max_eccentricity_tree):
            
            int_rad_idx = 1
            
            for j in range(0, len(Atomic_Agents[k])):
                
                if Atomic_Agents[k][j] in State_Nodes:
                    
                    shortest_lenght = len(nx.shortest_path(Atomic_Agents_Graphs[k], Atomic_Agents[k][0], Atomic_Agents[k][j]))
                    
                    for l in range(0, len(Atomic_Agents[k])):
                        
                        if Atomic_Agents[k][l] in Input_Nodes:
                            
                            if len(nx.shortest_path(Atomic_Agents_Graphs[k], Atomic_Agents[k][l], Atomic_Agents[k][j])) < shortest_lenght:
                                
                                shortest_lenght = len(nx.shortest_path(Atomic_Agents_Graphs[k], Atomic_Agents[k][l], Atomic_Agents[k][j]))


                    if shortest_lenght == m + 1:
                        
                        n_ui = number_states_eccentricity[m]
                        
                        positions[pos_idx] = [Atomic_Agents[k][j], ( longest_path-m) * radius * mt.cos(((2 * mt.pi * rad_idx)/(number_of_external_elements)) + (((2*mt.pi)/(number_of_external_elements))/(n_ui+1))*int_rad_idx), ( longest_path-m) * radius * mt.sin(((2 * mt.pi * rad_idx)/(number_of_external_elements)) + (((2*mt.pi)/(number_of_external_elements))/(n_ui+1))*int_rad_idx)]
                        
                        int_rad_idx += 1
                        
                        pos_idx += 1
  
        
        rad_idx +=1

    
# %%% Plot Radial Atomic Agents Graph


# !!!! This have to be modified w.r.t. the one used for the entire network graph to ensure a good graphical result
radius_circle = 0.35

sin_val_A = np.linalg.svd(A)
max_sin_val_A = np.amax(sin_val_A[1])

sin_val_B = np.linalg.svd(B)
max_sin_val_B = np.amax(sin_val_B[1])

plot_radial_atomic_agents_graph = True
save_radial_atomic_agents_graph = True

if plot_radial_atomic_agents_graph == True:

    plt.figure(figsize=(50, 50), dpi=100)
    
    ax = plt.gca()
    
    for k in range(0,len(Atomic_Agents)):
        
        if Atomic_Agents_Matrices[k] != []:
            
            for i in Atomic_Agents[k]:
                
                if i in State_Nodes:                   
                    
                    for j in State_Nodes:
                        
                        if j not in Atomic_Agents[k]:
                            
                            if A[i-number_of_inputs-1,j-number_of_inputs-1] != 0 and i != 0:
                                
                                for m in range(0,len(positions)): 
                                    
                                    if positions[m][0] == j:
                                        tail_idx = m
                                    if positions[m][0] == i:
                                        head_idx = m    
                                        
                                angle = mt.atan2(positions[head_idx][2]-positions[tail_idx][2],positions[head_idx][1]-positions[tail_idx][1])
                                x_shift = radius_circle*mt.cos(angle)
                                y_shift = radius_circle*mt.sin(angle)
                                plt.arrow(positions[tail_idx][1], positions[tail_idx][2], positions[head_idx][1]-positions[tail_idx][1]-x_shift, positions[head_idx][2]-positions[tail_idx][2]-y_shift, width=0.05, length_includes_head=True, color="cyan", alpha=abs(A[i-number_of_inputs-1,j-number_of_inputs-1])/max_sin_val_A)

        
    for k in range(0,len(Atomic_Agents)):
        
        if Atomic_Agents[k] != []:
            
            for i in Atomic_Agents[k]:
                
                if i in State_Nodes:                   
                    
                    for j in Atomic_Agents[k]:
                        
                        if j in State_Nodes:
                            
                            if A[i-number_of_inputs-1,j-number_of_inputs-1] != 0:
                                
                                for m in range(0,len(positions)): 
                                    
                                    if positions[m][0] == j:
                                        tail_idx = m
                                    if positions[m][0] == i:
                                        head_idx = m    
                                        
                                angle = mt.atan2(positions[head_idx][2]-positions[tail_idx][2],positions[head_idx][1]-positions[tail_idx][1])
                                x_shift = radius_circle*mt.cos(angle)
                                y_shift = radius_circle*mt.sin(angle)
                                plt.arrow(positions[tail_idx][1], positions[tail_idx][2], positions[head_idx][1]-positions[tail_idx][1]-x_shift, positions[head_idx][2]-positions[tail_idx][2]-y_shift, width=0.05, length_includes_head=True, color="black", alpha=abs(A[i-number_of_inputs-1,j-number_of_inputs-1])/max_sin_val_A)
     
    
    for k in range(0,len(Atomic_Agents)):
        
        if Atomic_Agents_Matrices[k] != []:
            
            for j in Atomic_Agents[k]:
                
                if j in Input_Nodes:                   
                    
                    for i in Atomic_Agents[k]:
                        
                        if i in State_Nodes:
                            
                            if B[i-number_of_inputs-1,j-1] != 0:
                                
                                for m in range(0,len(positions)): 
                                    
                                    if positions[m][0] == j:
                                        tail_idx = m
                                    if positions[m][0] == i:
                                        head_idx = m
                                        
                                angle = mt.atan2(positions[head_idx][2]-positions[tail_idx][2],positions[head_idx][1]-positions[tail_idx][1])
                                x_shift = radius_circle*mt.cos(angle)
                                y_shift = radius_circle*mt.sin(angle)
                                plt.arrow(positions[tail_idx][1], positions[tail_idx][2], positions[head_idx][1]-positions[tail_idx][1]-x_shift, positions[head_idx][2]-positions[tail_idx][2]-y_shift, width=0.05, length_includes_head=True, color="black", alpha=abs(B[i-number_of_inputs-1,j-1])/max_sin_val_B)
                                
    
    for k in range(0,len(positions)): 
       
        if positions[k] != []:
            
            if positions[k][0] in Input_Nodes:
                
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle, color='black', alpha=1)
                ax.add_patch(circle)
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle*0.9, color='w', alpha=1)
                ax.add_patch(circle)
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle*0.9, color='r', alpha=0.7)
                ax.add_patch(circle)
                plt.text(positions[k][1], positions[k][2], str(positions[k][0]), color="black", fontsize=80, horizontalalignment="center", verticalalignment="center")
            
            
            if positions[k][0] in State_Nodes:
                
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle, color='black', alpha=1)
                ax.add_patch(circle)
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle*0.9, color='w', alpha=1)
                ax.add_patch(circle)
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle*0.9, color='cyan', alpha=0.9)
                ax.add_patch(circle)
                plt.text(positions[k][1], positions[k][2], str(positions[k][0]-number_of_inputs), color="black", fontsize=80, horizontalalignment="center", verticalalignment="center")
  
            
    plt.axis("equal")
    plt.axis('off') 
    fig = plt.gcf()   
    plt.show() 
    if save_radial_atomic_agents_graph == True:
        fig.savefig("atomic_control_agents.pdf", transparent=True, dpi='figure')
        

# %% Additional sections to revise and Delete 
# %%% Plot Circular Tree of the original netwok using graphviz (Deprecated)

plot_network = False

if plot_network == True:

    pos = nx.nx_agraph.graphviz_layout(G_complete, prog="twopi", args="")
    plt.figure(figsize=(50, 50))
    nx.draw(G_complete, pos, node_size=0, alpha=0.5, node_color="blue", with_labels=True, font_size=48)
    for i in range(1, number_of_inputs+1):
        if i in pos:
            plt.scatter(pos[i][0], pos[i][1], s = 10000,color='r',alpha=1, )
    
    for i in range(number_of_inputs+1, number_of_states+number_of_inputs+1):
        if i in pos:
            plt.scatter(pos[i][0], pos[i][1], s = 10000,color='b' )
    
    plt.axis("equal")
    plt.show()

# %%% Plot Indidual Atomic Control Agents Graphs using graphviz (CHECK IF WE KEEP IT)

G_Atomic_Agents_Aggregated = nx.Graph()

for k in range(0, len(Atomic_Agents_Graphs)):
    G_Atomic_Agents_Aggregated.add_nodes_from(Atomic_Agents_Graphs[k].nodes())  
    G_Atomic_Agents_Aggregated.add_edges_from(Atomic_Agents_Graphs[k].edges())

plot_aggregated_agents_graphs = False

if plot_aggregated_agents_graphs == True:

    pos = nx.nx_agraph.graphviz_layout(G_Atomic_Agents_Aggregated, prog="neato", args="")
    plt.figure(figsize=(50, 50))
    nx.draw(G_Atomic_Agents_Aggregated, pos, node_size=0, alpha=0.5, node_color="blue", with_labels=True, font_size=48)
    
    for i in range(1, number_of_inputs+1):
        if i in pos:
            plt.scatter(pos[i][0], pos[i][1], s = 10000,color='r',alpha=1, )
    
    for i in range(number_of_inputs+1, number_of_states+number_of_inputs+1):
        if i in pos:
            plt.scatter(pos[i][0], pos[i][1], s = 10000,color='b' )
        
    plt.axis("equal")
    plt.show()   
    # plt.savefig(args, kwargs)
# %% Algorithmic Partitioning

N_atomic = len(Atomic_Agents)

# %%% Intra-Agent Weight

# We use Frobenius norm as a basis to construct this metric

# Initialize the empty list of intra-agents weights
W_intra = init_list_of_objects(N_atomic)

# Total intra-agents weight
W_intra_Total = 0

for k in range(0, N_atomic):
    
    W_intra_Total = W_intra_Total + np.linalg.norm(Atomic_Agents_Matrices[k][0][0], ord="fro")
    
# Intragent weight

for k in range(0, N_atomic):

    W_intra[k] = np.linalg.norm(Atomic_Agents_Matrices[k][0][0], ord="fro")/W_intra_Total
    
# %%% Inter-Agent Weight

# Initialize the empty list of inter-agents weights
W_inter = init_list_of_objects(N_atomic)

# Total intra-agents weight
W_inter_Total = 0


# %% Partitionig Problem


# Sort
Atomic_Agents.sort()
for k in range(0, len(Atomic_Agents)):
    Atomic_Agents[k].sort()

# %%% Atomic Agents Matrices
# Create empty list of atomic agents matrices
Atomic_Agents_Matrices = init_list_of_objects(number_of_inputs)

for k in range(0, len(Atomic_Agents)):
    
    # Detect the number of states and inputs
    nxi = 0
    nui = 0
        
    for i in range(0, len(Atomic_Agents[k])):
        
        if check_list(Input_Nodes, Atomic_Agents[k][i]) == True:              
            nui = nui + 1 
                
        elif check_list(State_Nodes, Atomic_Agents[k][i]) == True:        
            nxi = nxi + 1 
    
    
    Ai = np.full((nxi,nxi), 0, dtype='float64')
    Aij = np.full((nxi,number_of_states), 0, dtype='float64')   
    
    raw_idx = 0
    for i in Atomic_Agents[k]:
        
        if check_list(State_Nodes, i) == True:
            
            idx_node = index_list(State_Nodes, i)
            col_idx = 0 
            
            for j in range(0, number_of_states):                  
                
                if check_list(Atomic_Agents[k], State_Nodes[j]) == True:
                    Ai[raw_idx,col_idx] = A[idx_node,j]  
                    col_idx = col_idx + 1
                
                elif check_list(Atomic_Agents[k], State_Nodes[j]) == False:
                    Aij[raw_idx,j] = A[idx_node,j]
                    
            raw_idx = raw_idx + 1
        
    Atomic_Agents_Matrices[k]=[Ai,[],Aij]

# %%% Optimization VAriables

m = gp.Model("Partitioning")
delta = m.addMVar((N_atomic,N_atomic), vtype=GRB.BINARY)

# %%% Abstract coalition definition
N_atomic = len(Atomic_Agents)
# List of the agents
Control_Agents = init_list_of_objects(N_atomic)
Control_Agents_Matrices = init_list_of_objects(N_atomic)

Size_Atomic_Agents = init_list_of_objects(N_atomic)

for k in range(0, N_atomic):
    size_agent = 0
    for i in Atomic_Agents[k]:
        if check_list(State_Nodes,i) == True:
            size_agent += 1
    Size_Atomic_Agents[k] = size_agent
    
    
# %%% Control Agents Generalized Matrices

for k in range(0, N_atomic):
    A_si = gp.MQuadExpr.zeros((number_of_states,number_of_states))
    # A_si = np.empty((number_of_states,number_of_states))
    # A_si = np.full((number_of_states,number_of_states), 0, dtype='float64')
    raw_idx = 0
    # print(A_si)
    for i in range(0, N_atomic):    
        col_idx = 0        
        
        for j in range(0, N_atomic):
            # print(str(raw_idx))
            # print(str(raw_idx+Size_Atomic_Agents[i]))
            # print(str(col_idx))
            # print(str(col_idx+Size_Atomic_Agents[j]))
            A_si[raw_idx:raw_idx+Size_Atomic_Agents[i],col_idx:col_idx+Size_Atomic_Agents[j]] = A[raw_idx:raw_idx+Size_Atomic_Agents[i],col_idx:col_idx+Size_Atomic_Agents[j]]*(delta[i][k])*(delta[j][k])
            # print(A_si)
            col_idx = col_idx + Size_Atomic_Agents[j]                                    
        
        raw_idx = raw_idx + Size_Atomic_Agents[i]   
    
    Control_Agents_Matrices[k] = A_si

# %%% Inter-agents Interaction Matrices

Inter_Agents_Interaction_Matrices = init_list_of_objects(N_atomic)
for k in range(0,N_atomic):
    Inter_Agents_Interaction_Matrices[k] = init_list_of_objects(N_atomic)

for i in range(0,N_atomic):
    for j in range(0,N_atomic): 
        if i != j:
            Inter_Agents_Interaction_Matrices[i][j] = A - Control_Agents_Matrices[i] - Control_Agents_Matrices[j]
        elif i == j:
            Inter_Agents_Interaction_Matrices[i][j] = np.full((number_of_states,number_of_states), 0, dtype='float64') 

# %%% Total intra-agent interaction

# Total intra-agents weight
W_intra_Total = 0

for k in range(0, N_atomic):
    W_intra_Total  = W_intra_Total + Control_Agents_Matrices[k].sum()
   
# %%% Total inter-agent interaction

# Total intra-agents weight
W_inter_Total = 0

for i in range(0,N_atomic):
    for j in range(0,N_atomic): 
        W_inter_Total  = W_inter_Total + Inter_Agents_Interaction_Matrices[i][j].sum()


# %% Partitioning Optimization Problem

# %%% Objective function

obj = W_inter_Total - W_intra_Total

m.setObjective(obj)

# %%% Constraints

Constraints_Vector = delta.sum(axis=0) 

for k in range(0,N_atomic):
    m.addConstr(Constraints_Vector[k] == 1)

# %%% Run Optimization Problem

m.optimize()
all_vars = m.getVars()
print(all_vars)
values = m.getAttr("X", all_vars)

# %%% Optimization Problem



# M = np.full((number_of_states,N_atomic), 0, dtype='float64')

# raw_idx = 0
# for k in range(0, N_atomic):
#     for i in range(0, Size_Atomic_Agents[k]):
#         M[raw_idx,k] = 1
#         raw_idx += 1
    
    

# for k in range(0, N_atomic):
#     M = sp.linalg.block_diag(M, np.identity(Size_Atomic_Agents[k]))



# for i in range(0, N_atomic):
#     for j in range(0, N_atomic):
#      if delta[i][j] == True:
#          Control_Agents[i].append(Atomic_Agents[j])



    
















