import pickle as pk
import numpy as np

def create_empty_list(N):
    return [[] for _ in range(N)]

def create_empty_list_2D(x, y):
    empty_list = [[] for _ in range(x)]
    for i in range(0,x):
        empty_list[i] = [[] for _ in range(y)]
    return empty_list
