import pickle as pk
import numpy as np

def create_empty_list(N):
    return [[] for _ in range(N)]

def create_empty_list_2D(x, y):
    empty_list = [[] for _ in range(x)]
    for i in range(0,x):
        empty_list[i] = [[] for _ in range(y)]
    return empty_list

def load_linear_system(System_File):

    with open("Input_Data/" + System_File, 'rb') as f:
        System_List = pk.load(f)

    A = System_List[0].astype(np.float64)
    B = System_List[1].astype(np.float64)
    Weighted_Adjacency_Matrix = System_List[2]
    NUMBER_ATOMIC_AGENTS = System_List[3]

    return A, B, Weighted_Adjacency_Matrix, NUMBER_ATOMIC_AGENTS