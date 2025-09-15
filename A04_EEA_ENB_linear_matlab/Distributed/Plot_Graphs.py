# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 09:22:31 2024

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

# For the convex Hull
from scipy.spatial import ConvexHull

# %%% Load Local Custom Modules

#  Random Network Generation
from Random_Network_Generation import *

# Lists Manipulation
from Elementary_Support_Functions import *
     
# %%% Load .csv module


import csv
import pandas as pd

import math
# %% Import Data
data_frame = pd.read_csv("EXP_002_System.csv")
data_lists = data_frame.values.tolist()
# %%% Import System





number_of_inputs = int(data_lists[0][0])
number_of_states = int(data_lists[0][1])
Input_Nodes = np.arange(1,number_of_inputs+1)
State_Nodes = np.arange(number_of_inputs+1,number_of_inputs+number_of_states+1)
Input_Nodes_raw = np.array(data_lists[2][0:number_of_inputs])
for i in range(0,len(Input_Nodes)):
    Input_Nodes[i] = int(Input_Nodes_raw[i])
    
State_Nodes_raw = np.array(data_lists[4][0:number_of_states])
for i in range(0,len(State_Nodes)):
    State_Nodes[i] = int(State_Nodes_raw[i])


B = np.array(data_lists[6:6+number_of_states])
B = B[:,0:number_of_inputs]
A = np.array(data_lists[6+number_of_states+1:6+number_of_states+1+number_of_states])
A = A[:,0:number_of_states]


# %% Import Data
data_frame = pd.read_csv("EXP_002_AtomicAgents.csv")
data_lists = data_frame.values.tolist()
    
number_of_atomic_agents = int(data_lists[0][0])

# %%%
# List of the agents
Atomic_Agents = init_list_of_objects(number_of_atomic_agents)

# Create empty list of atomic agents matrices
Atomic_Agents_Matrices = init_list_of_objects(number_of_atomic_agents)

number_of_atomic_agents = int(data_lists[0][0])
Atomic_Agents= data_lists[2:2+number_of_atomic_agents] 




# %%%

for k in range(0,number_of_atomic_agents):
    for i in range(0,len(Atomic_Agents[k])):
        if math.isnan(Atomic_Agents[k][i]):
            Atomic_Agents[k][i] = []  

# Remove Empty Entries
for k in range(0,number_of_atomic_agents):
    while [] in Atomic_Agents[k]:
        Atomic_Agents[k].remove([])
        
        
for k in range(0,number_of_atomic_agents):
    for i in range(0,len(Atomic_Agents[k])):
        Atomic_Agents[k][i] = int(Atomic_Agents[k][i])  
       
# %%% 

agents_state_sizes = init_list_of_objects(number_of_atomic_agents)

for k in range(0, len(Atomic_Agents)):
    agents_state_sizes[k] = 0
    for i in Atomic_Agents[k]:
        if i in State_Nodes:
            agents_state_sizes[k] += 1
        
        
# %%%

Atomic_Agents_Trees = init_list_of_objects(number_of_inputs)
# List of the sub-graphs associated with the agents
Atomic_Agents_Graphs = init_list_of_objects(number_of_atomic_agents)


# Initialization of Atomic Agents Graphs
for i in range(0,len(Atomic_Agents_Graphs)):
    Atomic_Agents_Trees[i] = nx.Graph()
    Atomic_Agents_Graphs[i] = nx.Graph()       


# %%% Extract atomic agents matrices

data_frame = pd.read_csv("EXP_002_AtomicAgentsMatrices.csv")
data_lists = data_frame.values.tolist()


raw_idx = 0
for k in range(0,number_of_atomic_agents):
    A_i = np.array(data_lists[raw_idx:raw_idx+agents_state_sizes[k]])
    A_i = A_i[:,0:agents_state_sizes[k]]
    Atomic_Agents_Matrices[k] = [A_i,[],[]]      
    raw_idx = raw_idx+agents_state_sizes[k]  
    
# %%% Extract atomic agents interaction matrices

data_frame = pd.read_csv("EXP_002_AtomicAgentsInteractions.csv")
data_lists = data_frame.values.tolist()


raw_idx = 0
for k in range(0,number_of_atomic_agents):
    A_i = np.array(data_lists[raw_idx:raw_idx+agents_state_sizes[k]])
    A_i = A_i[:,0:number_of_states]
    Atomic_Agents_Matrices[k][2] = A_i      
    raw_idx = raw_idx+agents_state_sizes[k]  
    
# %%% Update Atomic Agents Trees and Graphs

for k in range(0, len(Atomic_Agents)):
    
    for i in Atomic_Agents[k]:
        
        Atomic_Agents_Trees[k].add_node(i)
        Atomic_Agents_Graphs[k].add_node(i)
        
        if i in Input_Nodes: 
            
            for j in Atomic_Agents[k]:
                
                if j in State_Nodes:                
                    # print("Input: ", i)
                    # print("State: ", j)
                    idx_j = index_list(State_Nodes, j)
                    idx_i = index_list(Input_Nodes, i)
                    if B[idx_j,idx_i] != 0:
                        # print("Bji: ", B[j-number_of_inputs-1,i-1])
                        Atomic_Agents_Trees[k].add_edge(i, j, weight=B[idx_j,idx_i])
                        Atomic_Agents_Graphs[k].add_edge(i, j, weight=B[idx_j,idx_i])   
        if i in State_Nodes:        
            
            for j in Atomic_Agents[k]:
                
                if j in State_Nodes:  
                    idx_j = index_list(State_Nodes, j)
                    idx_i = index_list(State_Nodes, i)
                    if A[idx_j,idx_i] != 0:
                        
                        Atomic_Agents_Trees[k].add_edge(i, j, weight=A[idx_j,idx_i])
                        Atomic_Agents_Graphs[k].add_edge(i, j, weight=A[idx_j,idx_i])                                   
# %% Network graph creation

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
save_network_map = False

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
                # try:
                #     if max_eccentricity_tree < len(nx.shortest_path(Atomic_Agents_Graphs[k], source=Atomic_Agents[k][0], target=Atomic_Agents[k][j],weight=1)):
                        
                #         max_eccentricity_tree = len(nx.shortest_path(Atomic_Agents_Graphs[k], source=Atomic_Agents[k][0], target=Atomic_Agents[k][j],weight=1))  
                # except:
                #     print("Error Line 444")
                
        number_states_eccentricity = np.full(max_eccentricity_tree, 0, dtype='float64')
 
        for j in range(0, len(Atomic_Agents[k])):
            
            if Atomic_Agents[k][j] in State_Nodes:
                
                # shortest_lenght = 2     # CONDITION TO AVOID ERRO, REMOVE !!!!
                try:
                    shortest_lenght = len(nx.shortest_path(Atomic_Agents_Graphs[k], source=Atomic_Agents[k][0], target=Atomic_Agents[k][j], weight=1))
                except:
                    print("Error Line 458")
                for l in range(0, len(Atomic_Agents[k])):
                    
                    if Atomic_Agents[k][l] in Input_Nodes:
                        
                        try:
                            if len(nx.shortest_path(Atomic_Agents_Graphs[k], Atomic_Agents[k][l], Atomic_Agents[k][j])) < shortest_lenght:
                                
                                shortest_lenght = len(nx.shortest_path(Atomic_Agents_Graphs[k], Atomic_Agents[k][l], Atomic_Agents[k][j]))    
                        except:
                            print("Error Line 470")    
                
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
radius_circle = 0.1

sin_val_A = np.linalg.svd(A)
max_sin_val_A = np.amax(sin_val_A[1])

sin_val_B = np.linalg.svd(B)
max_sin_val_B = np.amax(sin_val_B[1])

plot_radial_atomic_agents_graph = True
save_radial_atomic_agents_graph = False

if plot_radial_atomic_agents_graph == True:

    plt.figure(figsize=(50, 50), dpi=100)
    
    ax = plt.gca()
    
    # Convex Hull
    
    for k in range(0,len(Atomic_Agents)):
        if len(Atomic_Agents[k]) > 2:
            points = np.zeros([len(Atomic_Agents[k]),2])
            raw_idx = 0
            for i in Atomic_Agents[k]:
                for m in range(0,len(positions)):
                    if positions[m][0] == i:
                        points[raw_idx] = [positions[m][1], positions[m][2]]  
                        raw_idx += 1
            hull = ConvexHull(points)
            # for simplex in hull.simplices:
            #     ax.plot(points[simplex, 0], points[simplex, 1], 'k-')
            
            ax.fill(points[hull.vertices, 0], points[hull.vertices, 1],
                 facecolor="g", alpha=0.1 )
        # ax.plot(points[hull.vertices, 0], points[hull.vertices, 1], 'o', mec='r', color='none', lw=1, markersize=10)

    
    for k in range(0,len(Atomic_Agents)):
        
        if Atomic_Agents_Matrices[k] != []:
            
            for i in Atomic_Agents[k]:
                
                if i in State_Nodes:                   
                    
                    for j in State_Nodes:
                        
                        if j not in Atomic_Agents[k]:
                            idx_i = index_list(State_Nodes, i)
                            idx_j = index_list(State_Nodes, j)
                            
                            if A[idx_i,idx_j] != 0 and i != 0:
                                
                                for m in range(0,len(positions)): 
                                    
                                    if positions[m][0] == j:
                                        tail_idx = m
                                    if positions[m][0] == i:
                                        head_idx = m    
                                        
                                angle = mt.atan2(positions[head_idx][2]-positions[tail_idx][2],positions[head_idx][1]-positions[tail_idx][1])
                                x_shift = radius_circle*mt.cos(angle)
                                y_shift = radius_circle*mt.sin(angle)
                                plt.arrow(positions[tail_idx][1], positions[tail_idx][2], positions[head_idx][1]-positions[tail_idx][1]-x_shift, positions[head_idx][2]-positions[tail_idx][2]-y_shift, width=0.02, length_includes_head=True, color="cyan", alpha=abs(A[i-number_of_inputs-1,j-number_of_inputs-1])/max_sin_val_A)

        
    for k in range(0,len(Atomic_Agents)):
        
        if Atomic_Agents[k] != []:
            
            for i in Atomic_Agents[k]:
                
                if i in State_Nodes:                   
                    
                    for j in Atomic_Agents[k]:
                        
                        if j in State_Nodes:
                            
                            idx_i = index_list(State_Nodes, i)
                            idx_j = index_list(State_Nodes, j)
                            
                            if A[idx_i,idx_j] != 0:
                                
                                for m in range(0,len(positions)): 
                                    
                                    if positions[m][0] == j:
                                        tail_idx = m
                                    if positions[m][0] == i:
                                        head_idx = m    
                                        
                                angle = mt.atan2(positions[head_idx][2]-positions[tail_idx][2],positions[head_idx][1]-positions[tail_idx][1])
                                x_shift = radius_circle*mt.cos(angle)
                                y_shift = radius_circle*mt.sin(angle)
                                plt.arrow(positions[tail_idx][1], positions[tail_idx][2], positions[head_idx][1]-positions[tail_idx][1]-x_shift, positions[head_idx][2]-positions[tail_idx][2]-y_shift, width=0.02, length_includes_head=True, color="black", alpha=abs(A[idx_i,idx_j])/max_sin_val_A)
     
    
    for k in range(0,len(Atomic_Agents)):
        
        if Atomic_Agents_Matrices[k] != []:
            
            for j in Atomic_Agents[k]:
                
                if j in Input_Nodes:                   
                    
                    for i in Atomic_Agents[k]:
                        
                        if i in State_Nodes:
                            
                            idx_i = index_list(State_Nodes, i)
                            idx_j = index_list(Input_Nodes, j)
                            
                            if B[idx_i,idx_j] != 0:
                                
                                for m in range(0,len(positions)): 
                                    
                                    if positions[m][0] == j:
                                        tail_idx = m
                                    if positions[m][0] == i:
                                        head_idx = m
                                        
                                angle = mt.atan2(positions[head_idx][2]-positions[tail_idx][2],positions[head_idx][1]-positions[tail_idx][1])
                                x_shift = radius_circle*mt.cos(angle)
                                y_shift = radius_circle*mt.sin(angle)
                                plt.arrow(positions[tail_idx][1], positions[tail_idx][2], positions[head_idx][1]-positions[tail_idx][1]-x_shift, positions[head_idx][2]-positions[tail_idx][2]-y_shift, width=0.02, length_includes_head=True, color="black", alpha=abs(B[idx_i,idx_j])/max_sin_val_B)
                                
    
    for k in range(0,len(positions)): 
       
        if positions[k] != []:
            
            if positions[k][0] in Input_Nodes:
                
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle, color='black', alpha=1)
                ax.add_patch(circle)
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle*0.9, color='r', alpha=1)
                ax.add_patch(circle)
                plt.text(positions[k][1], positions[k][2], str(positions[k][0]), color="black", fontsize=24, horizontalalignment="center", verticalalignment="center")
            
            
            if positions[k][0] in State_Nodes:
                
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle, color='black', alpha=1)
                ax.add_patch(circle)
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle*0.9, color='b', alpha=1)
                ax.add_patch(circle)
                plt.text(positions[k][1], positions[k][2], str(positions[k][0]), color="black", fontsize=24, horizontalalignment="center", verticalalignment="center")
  
    
    
    ax.set_xticks(range(10))
    plt.axis("equal")
    plt.axis('off') 
    fig = plt.gcf()   
    plt.show() 
    if save_radial_atomic_agents_graph == True:
        fig.savefig("atomic_control_agents.pdf", transparent=True, dpi='figure')

# with open("EXP_002_System.csv", newline='') as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=' ', quotechar='|')
#     line_count = 0
#     for raw in csv_reader: 
#         if line_count == 0:
#             print("Number of inputs", raw[0][0])
#             print("Number of states", raw[0][1])
#         if raw[0][0] == "N":
#             print("Delimiter")
#         # print(raw[0][0])
#         line_count += 1






# %% CONTROL AGENTS

# %% Import Data
data_frame = pd.read_csv("EXP_002_ControlAgents.csv")
data_lists = data_frame.values.tolist()
    
number_of_control_agents = int(data_lists[0][0])

# %%%
# List of the agents
Control_Agents = init_list_of_objects(number_of_control_agents)

# Create empty list of control agents matrices
Control_Agents_Matrices = init_list_of_objects(number_of_control_agents)

number_of_control_agents = int(data_lists[0][0])
Control_Agents= data_lists[2:2+number_of_control_agents] 




# %%%

for k in range(0,number_of_control_agents):
    for i in range(0,len(Control_Agents[k])):
        if math.isnan(Control_Agents[k][i]):
            Control_Agents[k][i] = []  

# Remove Empty Entries
for k in range(0,number_of_control_agents):
    while [] in Control_Agents[k]:
        Control_Agents[k].remove([])
        
        
for k in range(0,number_of_control_agents):
    for i in range(0,len(Control_Agents[k])):
        Control_Agents[k][i] = int(Control_Agents[k][i])  
       
# %%% 

agents_state_sizes = init_list_of_objects(number_of_control_agents)

for k in range(0, len(Control_Agents)):
    agents_state_sizes[k] = 0
    for i in Control_Agents[k]:
        if i in State_Nodes:
            agents_state_sizes[k] += 1
        
        
# %%%

Control_Agents_Trees = init_list_of_objects(number_of_inputs)
# List of the sub-graphs associated with the agents
Control_Agents_Graphs = init_list_of_objects(number_of_control_agents)


# Initialization of Control Agents Graphs
for i in range(0,len(Control_Agents_Graphs)):
    Control_Agents_Trees[i] = nx.Graph()
    Control_Agents_Graphs[i] = nx.Graph()       


# %%% Extract control agents matrices

data_frame = pd.read_csv("EXP_002_ControlAgentsMatrices.csv")
data_lists = data_frame.values.tolist()


raw_idx = 0
for k in range(0,number_of_control_agents):
    A_i = np.array(data_lists[raw_idx:raw_idx+agents_state_sizes[k]])
    A_i = A_i[:,0:agents_state_sizes[k]]
    Control_Agents_Matrices[k] = [A_i,[],[]]      
    raw_idx = raw_idx+agents_state_sizes[k]  
    
# %%% Extract control agents interaction matrices

data_frame = pd.read_csv("EXP_002_ControlAgentsInteractions.csv")
data_lists = data_frame.values.tolist()


raw_idx = 0
for k in range(0,number_of_control_agents):
    A_i = np.array(data_lists[raw_idx:raw_idx+agents_state_sizes[k]])
    A_i = A_i[:,0:number_of_states]
    Control_Agents_Matrices[k][2] = A_i      
    raw_idx = raw_idx+agents_state_sizes[k]  
    
# %%% Update Control Agents Trees and Graphs

for k in range(0, len(Control_Agents)):
    
    for i in Control_Agents[k]:
        
        Control_Agents_Trees[k].add_node(i)
        Control_Agents_Graphs[k].add_node(i)
        
        if i in Input_Nodes: 
            
            for j in Control_Agents[k]:
                
                if j in State_Nodes:                
                    # print("Input: ", i)
                    # print("State: ", j)
                    idx_j = index_list(State_Nodes, j)
                    idx_i = index_list(Input_Nodes, i)
                    if B[idx_j,idx_i] != 0:
                        # print("Bji: ", B[j-number_of_inputs-1,i-1])
                        Control_Agents_Trees[k].add_edge(i, j, weight=B[idx_j,idx_i])
                        Control_Agents_Graphs[k].add_edge(i, j, weight=B[idx_j,idx_i])   
        if i in State_Nodes:        
            
            for j in Control_Agents[k]:
                
                if j in State_Nodes:  
                    idx_j = index_list(State_Nodes, j)
                    idx_i = index_list(State_Nodes, i)
                    if A[idx_j,idx_i] != 0:
                        
                        Control_Agents_Trees[k].add_edge(i, j, weight=A[idx_j,idx_i])
                        Control_Agents_Graphs[k].add_edge(i, j, weight=A[idx_j,idx_i])  


# %%% Position of nodes

# List of the positions of the nodes
positions = init_list_of_objects(number_of_states + number_of_inputs)

# %%% Determination of the number of rings of the circular graph

# Number of sections of the external radius
number_of_external_elements = len(Control_Agents) 

pos_idx = 0

# Basic radius unit used throughout the networks
radius = 1

rad_idx = 0
longest_path = 0

# Determination of the number of rings of the circular graph
# Determination of the number of rings of the circular graph
for k in range(0,len(Control_Agents)): 
    
    for j in range(0, len(Control_Agents[k])):

        if Control_Agents[k][j] in State_Nodes:

            shortest_lenght = len(nx.shortest_path(Control_Agents_Graphs[k], source=Control_Agents[k][0], target=Control_Agents[k][j], weight=1))
    
            if shortest_lenght > longest_path:
                
                longest_path = shortest_lenght
# %%% Assignment of the Position of nodes
                    
for k in range(0,len(Control_Agents)): 
    
    # input nodes
    
    if Control_Agents[k] != []:

        n_ui = 0
        
        for j in range(0, len(Control_Agents[k])):
            
            if Control_Agents[k][j] in Input_Nodes:
                
                n_ui += 1
        
        
        k_ui = 1       
        
        for j in range(0, len(Control_Agents[k])):
            
            # index internal division
            if Control_Agents[k][j] in Input_Nodes:
                
                positions[pos_idx] = [Control_Agents[k][j],  (longest_path)*radius * mt.cos(((2 * mt.pi * rad_idx)/(number_of_external_elements)) + (((2*mt.pi)/(number_of_external_elements))/(n_ui+1))*k_ui), (longest_path)*radius * mt.sin(((2 * mt.pi * rad_idx)/(number_of_external_elements)) + (((2*mt.pi)/(number_of_external_elements))/(n_ui+1))*k_ui)]
                
                k_ui += 1 
                
                pos_idx += 1
                
        
        # State Nodes
        n_xi = 0
        
        max_eccentricity_tree = 0
        
        for j in range(0, len(Control_Agents[k])):
            
            if Control_Agents[k][j] in State_Nodes:
                
                if max_eccentricity_tree < len(nx.shortest_path(Control_Agents_Graphs[k], source=Control_Agents[k][0], target=Control_Agents[k][j],weight=1)):
                    
                    max_eccentricity_tree = len(nx.shortest_path(Control_Agents_Graphs[k], source=Control_Agents[k][0], target=Control_Agents[k][j],weight=1))
                # try:
                #     if max_eccentricity_tree < len(nx.shortest_path(Control_Agents_Graphs[k], source=Control_Agents[k][0], target=Control_Agents[k][j],weight=1)):
                        
                #         max_eccentricity_tree = len(nx.shortest_path(Control_Agents_Graphs[k], source=Control_Agents[k][0], target=Control_Agents[k][j],weight=1))  
                # except:
                #     print("Error Line 444")
                
        number_states_eccentricity = np.full(max_eccentricity_tree, 0, dtype='float64')
 
        for j in range(0, len(Control_Agents[k])):
            
            if Control_Agents[k][j] in State_Nodes:
                
                # shortest_lenght = 2     # CONDITION TO AVOID ERRO, REMOVE !!!!
                try:
                    shortest_lenght = len(nx.shortest_path(Control_Agents_Graphs[k], source=Control_Agents[k][0], target=Control_Agents[k][j], weight=1))
                except:
                    print("Error Line 458")
                for l in range(0, len(Control_Agents[k])):
                    
                    if Control_Agents[k][l] in Input_Nodes:
                        
                        try:
                            if len(nx.shortest_path(Control_Agents_Graphs[k], Control_Agents[k][l], Control_Agents[k][j])) < shortest_lenght:
                                
                                shortest_lenght = len(nx.shortest_path(Control_Agents_Graphs[k], Control_Agents[k][l], Control_Agents[k][j]))    
                        except:
                            print("Error Line 470")    
                
                eccentricity_state = shortest_lenght

                number_states_eccentricity[eccentricity_state-1] = number_states_eccentricity[eccentricity_state-1] + 1
                
        
        for m in range(0, max_eccentricity_tree):
            
            int_rad_idx = 1
            
            for j in range(0, len(Control_Agents[k])):
                
                if Control_Agents[k][j] in State_Nodes:
                    
                    shortest_lenght = len(nx.shortest_path(Control_Agents_Graphs[k], Control_Agents[k][0], Control_Agents[k][j]))
                    
                    for l in range(0, len(Control_Agents[k])):
                        
                        if Control_Agents[k][l] in Input_Nodes:
                            
                            if len(nx.shortest_path(Control_Agents_Graphs[k], Control_Agents[k][l], Control_Agents[k][j])) < shortest_lenght:
                                
                                shortest_lenght = len(nx.shortest_path(Control_Agents_Graphs[k], Control_Agents[k][l], Control_Agents[k][j]))


                    if shortest_lenght == m + 1:
                        
                        n_ui = number_states_eccentricity[m]
                        
                        positions[pos_idx] = [Control_Agents[k][j], ( longest_path-m) * radius * mt.cos(((2 * mt.pi * rad_idx)/(number_of_external_elements)) + (((2*mt.pi)/(number_of_external_elements))/(n_ui+1))*int_rad_idx), ( longest_path-m) * radius * mt.sin(((2 * mt.pi * rad_idx)/(number_of_external_elements)) + (((2*mt.pi)/(number_of_external_elements))/(n_ui+1))*int_rad_idx)]
                        
                        int_rad_idx += 1
                        
                        pos_idx += 1
  
        
        rad_idx +=1

    
# %%% Plot Radial Control Agents Graph


# !!!! This have to be modified w.r.t. the one used for the entire network graph to ensure a good graphical result
radius_circle = 0.1

sin_val_A = np.linalg.svd(A)
max_sin_val_A = np.amax(sin_val_A[1])

sin_val_B = np.linalg.svd(B)
max_sin_val_B = np.amax(sin_val_B[1])

plot_radial_control_agents_graph = True
save_radial_control_agents_graph = False

if plot_radial_control_agents_graph == True:

    plt.figure(figsize=(50, 50), dpi=100)
    
    ax = plt.gca()
    
    # Convex Hull
    
    for k in range(0,len(Control_Agents)):
        if len(Control_Agents[k]) > 2:
            points = np.zeros([len(Control_Agents[k]),2])
            raw_idx = 0
            for i in Control_Agents[k]:
                for m in range(0,len(positions)):
                    if positions[m][0] == i:
                        points[raw_idx] = [positions[m][1], positions[m][2]]  
                        raw_idx += 1
            hull = ConvexHull(points)
            # for simplex in hull.simplices:
            #     ax.plot(points[simplex, 0], points[simplex, 1], 'k-')
            
            ax.fill(points[hull.vertices, 0], points[hull.vertices, 1],
                 facecolor="g", alpha=0.1 )
        # ax.plot(points[hull.vertices, 0], points[hull.vertices, 1], 'o', mec='r', color='none', lw=1, markersize=10)

    
    
    for k in range(0,len(Control_Agents)):
        
        if Control_Agents_Matrices[k] != []:
            
            for i in Control_Agents[k]:
                
                if i in State_Nodes:                   
                    
                    for j in State_Nodes:
                        
                        if j not in Control_Agents[k]:
                            idx_i = index_list(State_Nodes, i)
                            idx_j = index_list(State_Nodes, j)
                            
                            if A[idx_i,idx_j] != 0 and i != 0:
                                
                                for m in range(0,len(positions)): 
                                    
                                    if positions[m][0] == j:
                                        tail_idx = m
                                    if positions[m][0] == i:
                                        head_idx = m    
                                        
                                angle = mt.atan2(positions[head_idx][2]-positions[tail_idx][2],positions[head_idx][1]-positions[tail_idx][1])
                                x_shift = radius_circle*mt.cos(angle)
                                y_shift = radius_circle*mt.sin(angle)
                                plt.arrow(positions[tail_idx][1], positions[tail_idx][2], positions[head_idx][1]-positions[tail_idx][1]-x_shift, positions[head_idx][2]-positions[tail_idx][2]-y_shift, width=0.02, length_includes_head=True, color="cyan", alpha=abs(A[i-number_of_inputs-1,j-number_of_inputs-1])/max_sin_val_A)

        
    for k in range(0,len(Control_Agents)):
        
        if Control_Agents[k] != []:
            
            for i in Control_Agents[k]:
                
                if i in State_Nodes:                   
                    
                    for j in Control_Agents[k]:
                        
                        if j in State_Nodes:
                            
                            idx_i = index_list(State_Nodes, i)
                            idx_j = index_list(State_Nodes, j)
                            
                            if A[idx_i,idx_j] != 0:
                                
                                for m in range(0,len(positions)): 
                                    
                                    if positions[m][0] == j:
                                        tail_idx = m
                                    if positions[m][0] == i:
                                        head_idx = m    
                                        
                                angle = mt.atan2(positions[head_idx][2]-positions[tail_idx][2],positions[head_idx][1]-positions[tail_idx][1])
                                x_shift = radius_circle*mt.cos(angle)
                                y_shift = radius_circle*mt.sin(angle)
                                plt.arrow(positions[tail_idx][1], positions[tail_idx][2], positions[head_idx][1]-positions[tail_idx][1]-x_shift, positions[head_idx][2]-positions[tail_idx][2]-y_shift, width=0.02, length_includes_head=True, color="black", alpha=abs(A[idx_i,idx_j])/max_sin_val_A)
     
    
    for k in range(0,len(Control_Agents)):
        
        if Control_Agents_Matrices[k] != []:
            
            for j in Control_Agents[k]:
                
                if j in Input_Nodes:                   
                    
                    for i in Control_Agents[k]:
                        
                        if i in State_Nodes:
                            
                            idx_i = index_list(State_Nodes, i)
                            idx_j = index_list(Input_Nodes, j)
                            
                            if B[idx_i,idx_j] != 0:
                                
                                for m in range(0,len(positions)): 
                                    
                                    if positions[m][0] == j:
                                        tail_idx = m
                                    if positions[m][0] == i:
                                        head_idx = m
                                        
                                angle = mt.atan2(positions[head_idx][2]-positions[tail_idx][2],positions[head_idx][1]-positions[tail_idx][1])
                                x_shift = radius_circle*mt.cos(angle)
                                y_shift = radius_circle*mt.sin(angle)
                                plt.arrow(positions[tail_idx][1], positions[tail_idx][2], positions[head_idx][1]-positions[tail_idx][1]-x_shift, positions[head_idx][2]-positions[tail_idx][2]-y_shift, width=0.02, length_includes_head=True, color="black", alpha=abs(B[idx_i,idx_j])/max_sin_val_B)
                                
    
    for k in range(0,len(positions)): 
       
        if positions[k] != []:
            
            if positions[k][0] in Input_Nodes:
                
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle, color='black', alpha=1)
                ax.add_patch(circle)
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle*0.9, color='r', alpha=1)
                ax.add_patch(circle)
                plt.text(positions[k][1], positions[k][2], str(positions[k][0]), color="black", fontsize=24, horizontalalignment="center", verticalalignment="center")
            
            
            if positions[k][0] in State_Nodes:
                
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle, color='black', alpha=1)
                ax.add_patch(circle)
                circle = plt.Circle((positions[k][1], positions[k][2]), radius_circle*0.9, color='b', alpha=1)
                ax.add_patch(circle)
                plt.text(positions[k][1], positions[k][2], str(positions[k][0]), color="black", fontsize=24, horizontalalignment="center", verticalalignment="center")
  
    
    
    ax.set_xticks(range(10))
    plt.axis("equal")
    plt.axis('off') 
    fig = plt.gcf()   
    plt.show() 
    if save_radial_control_agents_graph == True:
        fig.savefig("control_control_agents.pdf", transparent=True, dpi='figure')

# with open("EXP_002_System.csv", newline='') as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=' ', quotechar='|')
#     line_count = 0
#     for raw in csv_reader: 
#         if line_count == 0:
#             print("Number of inputs", raw[0][0])
#             print("Number of states", raw[0][1])
#         if raw[0][0] == "N":
#             print("Delimiter")
#         # print(raw[0][0])
#         line_count += 1