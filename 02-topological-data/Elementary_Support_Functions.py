# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 10:18:00 2024

@author: ariccardi
"""

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