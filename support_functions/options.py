import argparse
import json

def parse_arguments():


    parser = argparse.ArgumentParser(prefix_chars='--')

    parser.add_argument('--electrical_areas', type=json.loads, default="[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]",
                         help='List of electrical areas to simulate')

    parser.add_argument('--control_time_step', type=float, default=0.5,
                         help='Control time step in seconds')
    
    parser.add_argument('--number_hours', type=int, default=24,
                         help='Number of hours to simulate')
    
    parser.add_argument('--model', type=str, default="linear",
                         help='Type of model to use for the network dynamics, e.g., "linear"')

    parser.add_argument('--control_strategy', type=str, default="centralized",
                         help='Control strategy to use, e.g., "centralized" or "distributed"')
    
    parser.add_argument('--partitioning_strategy', type=str, default="none",
                         help='Partitioning strategy to use for distributed control, e.g., "none", "spectral_clustering", "k_means", etc.')

    parser.add_argument('--simulation_horizon', type=int, default=100,
                         help='Number of time steps to simulate')
    
    parser.add_argument('--prediction_horizon', type=int, default=10,
                         help='Number of time steps to use for the prediction horizon in MPC')  
    
    parser.add_argument('--state_weighting_matrix', type=json.loads, default="[]",
                         help='State weighting matrix for the MPC cost function, provided as a JSON-formatted string representing a 2D list (matrix)')
    
    parser.add_argument('--input_weighting_matrix', type=json.loads, default="[]",
                         help='Input weighting matrix for the MPC cost function, provided as a JSON-formatted string representing a 2D list (matrix)')

    parser.add_argument('--consensus_treshold', type=float, default=1e-6,
                         help='Threshold for consensus convergence in the distributed MPC algorithm')   

    parser.add_argument('--preprocess_data', type=bool, default=False,
                         help='Whether to preprocess the data, only required if control time step or number of hours to simulates changes')
    
    parser.add_argument('--plot_data', type=bool, default=True,
                         help='Whether to plot the data')
    
    parser.add_argument('--store_data', type=bool, default=True,
                         help='Whether to store the preprocessed data')
    
    args = parser.parse_args()

    return args