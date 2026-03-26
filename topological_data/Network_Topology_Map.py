# %%% Load modules

# For linear algebra
import numpy as np

# For plots
import matplotlib.pyplot as plt
import matplotlib.ticker as tk

# Math module
import math as mt

# For data
import geopandas as gpd
import pandas as pd

import os

# %% Elementary support functions

# %% Function to create empty lists        
        
def init_list_of_objects(size):
    list_of_objects = list()
    for i in range(0,size):
        list_of_objects.append( list() ) #different object reference each time
    return list_of_objects      


# %% Function to get indexes of elements from lists

def index_2d(my_list, v):
    for i in range(len(my_list)):
        for j in range(len(my_list[i])):
            if v == my_list[i][j]:
                return (i, j)
    
            
# %% Function to check if an element belongs to a 2D list

def check_2d(my_list, v):
    condition = False
    for i in range(len(my_list)):
        for j in range(len(my_list[i])):
            if v == my_list[i][j]:
                condition = True
    return condition
 
    
 # %% Function to check if an element belongs to a list

def check_list(my_list, v):
    condition = False
    for i in range(len(my_list)):
        if v == my_list[i]:
            condition = True
    return condition

# %% Function to get indexes of elements from list one dimensional

def index_list(my_list, v):
    for i in range(len(my_list)):
        if v == my_list[i]:
                return i


# %% Computation of topological data

# This funciton can be refined to plot only the desired topology
def compute_topological_data(plot_map, export_map):

    points_file_name = "Centroids.csv"
    adj_matrix_file_name = "Adj.csv"
    adj_wei_matrix_file_name = "Adj_W.csv"

    # %% Import benchmark areas



    df_areas = pd.read_csv("Data/Benchmark_Areas.csv")

    benchmark_areas = {}

    for pos_idx in range(0, len(df_areas)):
        country_ISO = df_areas.iloc[pos_idx].AFF_ISO
        country_ID = df_areas.iloc[pos_idx].ID
        # Handling special nomenclature for Greece in the dataset
        if country_ISO == "GR":
            benchmark_areas["EL"] = country_ID 
        else:
            benchmark_areas[country_ISO] = country_ID 

    # %% Import complementary benchmark areas

    df_areas_Complementary = pd.read_csv("Data/Benchmark_Areas_Complementary.csv")

    benchmark_areas_Complementary = {}

    for pos_idx in range(0, len(df_areas_Complementary)):
        country_ISO_Complementary = df_areas_Complementary.iloc[pos_idx].AFF_ISO
        country_ID_Complementary = df_areas_Complementary.iloc[pos_idx].ID
        benchmark_areas_Complementary[country_ISO_Complementary] = country_ID_Complementary 

    # %% Topological data

    # EEA Map
    gdf_rg = gpd.read_file("Data/NUTS_RG_01M_2021_3035_LEVL_0.json")
    gdf_rg = gdf_rg.sort_values('id')

    # Get elements in the benchmark_areas dictionary
    eea_areas_rg = gdf_rg[gdf_rg.isin(benchmark_areas.keys()).id].copy()
    # eea_areas_rg = eea_areas_rg.set_crs('epsg:3857')
    eea_areas_rg = eea_areas_rg.sort_values('id')  

    # EEA Map
    gdf_rg_Complementary = gpd.read_file("Data/NUTS_RG_01M_2021_3035_LEVL_0.json")
    gdf_rg_Complementary = gdf_rg_Complementary.sort_values('id')
    # Get elements in the Complementary benchmark_areas dictionary
    eea_areas_rg_Complementary = gdf_rg_Complementary[gdf_rg_Complementary.isin(benchmark_areas_Complementary.keys()).id].copy()
    # eea_areas_rg = eea_areas_rg.set_crs('epsg:3857')
    eea_areas_rg_Complementary = eea_areas_rg_Complementary.sort_values('id')  

    # %% Compute centroids

    representative_points = eea_areas_rg.representative_point()
    centroids = eea_areas_rg.centroid

    # For France select representative point instead of centroid
    centroids[13] = representative_points[13]

    # Build list of centroids from geoseries
    centroids_list = init_list_of_objects(len(representative_points))

    for pos_idx in range(0,len(centroids_list)):
        point = centroids.iloc[pos_idx]
        centroids_list[pos_idx] = [pos_idx, point.x, point.y]   

    # %% Adjacency data

    df_adjacency = pd.read_csv("Data/Adjacency_List.csv")
    adjacency_list = df_adjacency.values.tolist()


    # %% Position of nodes

    # List of the positions of the nodes
    nodes = init_list_of_objects(len(representative_points))

    id_keys = list(benchmark_areas.keys())
    df_nodes = pd.DataFrame(columns=['Area', 'ID', 'X', 'Y', 'AFF_ISO'])

    for pos_idx in range(0,len(representative_points)):
        mask = eea_areas_rg['id'] == id_keys[pos_idx]
        pos = np.flatnonzero(mask)
        point = eea_areas_rg.iloc[pos].centroid
        df_nodes.loc[pos_idx] = [df_areas.iloc[pos_idx].Area, 
                                df_areas.iloc[pos_idx].ID,
                                point.x.iloc[0]/1e6, point.y.iloc[0]/1e6,
                                df_areas.iloc[pos_idx].AFF_ISO]
        point = centroids.iloc[pos]
        nodes[pos_idx] = [pos_idx + 1, point.x, point.y, id_keys[pos_idx]]
        
        # Id correction for Greece
        if id_keys[pos_idx] == 'EL':
            nodes[pos_idx] = [pos_idx + 1, point.x, point.y, 'GR']
    

    # %% Build adjacency matrix 

    adj_matrix = np.zeros((len(nodes),len(nodes)))    
    adj_wei_matrix = np.zeros((len(nodes),len(nodes)))  

    for i in range(0,len(adjacency_list)):
        for j in range(2,len(adjacency_list[i])):
            if np.isnan(adjacency_list[i][j]) == False:
                agent_idx = int(adjacency_list[i][j]) - 1
                
                distance_ij = np.sqrt(np.power(nodes[agent_idx][1].iloc[0] - nodes[i][1].iloc[0],2) + 
                                    np.power(nodes[agent_idx][2].iloc[0] - nodes[i][2].iloc[0],2))
                
                adj_matrix[i,agent_idx] = 1
                adj_wei_matrix[i,agent_idx] = distance_ij/1e6
    
    # %% Export data

    df_nodes.to_csv(points_file_name, index=False)

    df_adj_matrix = pd.DataFrame(adj_matrix)
    df_adj_wei_matrix = pd.DataFrame(adj_wei_matrix)

    df_adj_matrix.to_csv(adj_matrix_file_name, header = False, index = False)
    df_adj_wei_matrix.to_csv(adj_wei_matrix_file_name, header = False, index = False)

    # %% Plot map

    # fig = plt.figure()
    # 


    # ax = gdf_rg.plot(figsize=(50, 50), color="lightgrey", edgecolor="black", alpha=0.3,zorder=-1)
    # eea_areas_rg.plot(figsize=(50, 50), color="forestgreen", edgecolor="black", alpha=0.3,zorder=0)
    # Fig_Ref = plt.figure(figsize=(8, 6))

    fig, ax = plt.subplots(figsize=(50, 50))

    eea_areas_rg.plot(ax=ax, color="forestgreen", edgecolor="black", alpha=0.3,zorder=0)
    # ax = plt.gca()
    # map_fig = plt.gcf()
    eea_areas_rg_Complementary.plot(ax=ax, color="dimgrey", edgecolor="black", alpha=0.3,zorder=0)
    # Fig_Ref = plt.gcf()

    # ax.set_xlim([2600000, 6000000])
    # ax.set_ylim([1400000, 5450000])
    # ax = Fig_Ref.axes
    # Plot nodes on map

    radius_circle = 100000/1.25
    font_size = 40


    # Max Lenght
    max_distance = 0;
    for i in range(0,len(adjacency_list)):
        for j in range(2,len(adjacency_list[i])):
            if np.isnan(adjacency_list[i][j]) == False:
                agent_idx = int(adjacency_list[i][j]) - 1
                
                distance_ij = np.sqrt(np.power(nodes[agent_idx][1].iloc[0] - nodes[i][1].iloc[0],2) + 
                                    np.power(nodes[agent_idx][2].iloc[0] - nodes[i][2].iloc[0],2))
                if distance_ij > max_distance:
                    max_distance = distance_ij
                    
    # Max Distance Ratio
    max_distance_ratio = 0;
    for i in range(0,len(adjacency_list)):
        for j in range(2,len(adjacency_list[i])):
            if np.isnan(adjacency_list[i][j]) == False:
                agent_idx = int(adjacency_list[i][j])
                
                distance_ij = np.sqrt(np.power(nodes[agent_idx-1][1].iloc[0] - nodes[i][1].iloc[0],2) + 
                                    np.power(nodes[agent_idx-1][2].iloc[0] - nodes[i][2].iloc[0],2))
                if max_distance/distance_ij > max_distance_ratio:
                    max_distance_ratio = max_distance/distance_ij
                    

    # Plot Graph
    if plot_map == True:

        # ax = plt.gca()
        # fig = plt.gcf()
        # ax = plt.gca()
            
        for i in range(0,len(adjacency_list)):
            for j in range(2,len(adjacency_list[i])):
                if np.isnan(adjacency_list[i][j]) == False:
                    agent_idx = int(adjacency_list[i][j])
                    
                    distance_ij = np.sqrt(np.power(nodes[agent_idx-1][1].iloc[0] - nodes[i][1].iloc[0],2) + 
                                        np.power(nodes[agent_idx-1][2].iloc[0] - nodes[i][2].iloc[0],2))
                    plt.arrow(nodes[i][1].iloc[0], nodes[i][2].iloc[0], 
                            nodes[agent_idx-1][1].iloc[0] - nodes[i][1].iloc[0], 
                            nodes[agent_idx-1][2].iloc[0] - nodes[i][2].iloc[0],
                            width=100000/3.5, head_width = 0.2, length_includes_head=True,
                            color="white", alpha=0.5,zorder=2)
                    plt.arrow(nodes[i][1].iloc[0], nodes[i][2].iloc[0], 
                            nodes[agent_idx-1][1].iloc[0] - nodes[i][1].iloc[0], 
                            nodes[agent_idx-1][2].iloc[0] - nodes[i][2].iloc[0],
                            width=100000/3.5, head_width = 0.2, length_includes_head=True,
                            color="blue", alpha=(max_distance/distance_ij/max_distance_ratio),zorder=3)    
                    
        
        for pos_idx in range(0,len(nodes)): 
            
            circle = plt.Circle((nodes[pos_idx][1].iloc[0], nodes[pos_idx][2].iloc[0]), radius_circle, color='black', alpha=1,zorder=4)
            ax.add_patch(circle)
            circle = plt.Circle((nodes[pos_idx][1].iloc[0], nodes[pos_idx][2].iloc[0]), radius_circle*0.9, color='white', alpha=1,zorder=5)
            ax.add_patch(circle)
            circle = plt.Circle((nodes[pos_idx][1].iloc[0], nodes[pos_idx][2].iloc[0]), radius_circle*0.9, color='red', alpha=0.5,zorder=6)
            ax.add_patch(circle)
            plt.text(nodes[pos_idx][1].iloc[0], nodes[pos_idx][2].iloc[0], str(nodes[pos_idx][3]), color="black", fontsize=font_size, family="Times New Roman",horizontalalignment="center", verticalalignment="center",zorder=7)
            
        ax.set_xlim([2600000, 6000000])
        ax.set_ylim([1400000, 5450000])
        ax.ticklabel_format(useMathText=True)
        
        ax.tick_params(axis='x', which = 'both', labelfontfamily = 'Times New Roman', labelsize=50)   
        ax.tick_params(axis='y', which = 'both', labelfontfamily = 'Times New Roman', labelsize=50)
        ax.xaxis.get_offset_text().set_fontsize(50)
        ax.yaxis.get_offset_text().set_fontsize(50)
        plt.rcParams["font.family"] = 'Times New Roman'
        for x in ax.spines.values():
            x.set_linewidth(3)
        

        
        fig = plt.gcf()
        
        if export_map == True:
            
            map_file_name = "figures/EEA-ENB_Topology_Map.png"
            fig.savefig(map_file_name, transparent=True, bbox_inches='tight', dpi='figure')
            map_file_name = "figures/EEA-ENB_Topology_Map.pdf"
            fig.savefig(map_file_name, transparent=True, bbox_inches='tight', dpi='figure')

# %%
