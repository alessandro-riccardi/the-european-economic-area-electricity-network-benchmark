import numpy as np
import pandas as pd
import os


def import_electricity_data(LIST_ATOMIC_AGENTS, SIMULATION_HORIZON, PREDICTION_HORIZON):
    
    current_folder = os.path.dirname(os.path.abspath(__file__))

    dispatchable_capacities = np.loadtxt(os.path.normpath(os.path.join('electricity_data', 'capacities_list.csv')), delimiter=',')

    NUMBER_ATOMIC_AGENTS = len(LIST_ATOMIC_AGENTS)

    # Load signals
    # Aggregated data
    MEASURED_LOAD_NETWORK = (np.loadtxt(os.path.normpath(os.path.join('electricity_data', 'measured_load_dataset.csv')), delimiter=',')).T
    MEASURED_RENEWABLE_NETWORK = (np.loadtxt(os.path.normpath(os.path.join('electricity_data', 'measured_renewable_dataset.csv')), delimiter=',')).T

    MEASURED_LOAD = np.zeros((NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+PREDICTION_HORIZON))
    MEASURED_RENEWABLE = np.zeros((NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+PREDICTION_HORIZON))

    # Incremental data
    MEASURED_LOAD_INCREMENTS_NETWORK = (np.loadtxt(os.path.normpath(os.path.join('electricity_data', 'measured_load_increment_dataset.csv')), delimiter=',')).T
    MEASURED_RENEWABLE_INCREMENTS_NETWORK = (np.loadtxt(os.path.normpath(os.path.join('electricity_data', 'measured_renewable_increment_dataset.csv')), delimiter=',')).T

    MEASURED_LOAD_INCREMENTS = np.zeros((NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+PREDICTION_HORIZON))
    MEASURED_RENEWABLE_INCREMENTS = np.zeros((NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+PREDICTION_HORIZON))

    FORECAST_LOAD_INCREMENTS_NETWORK = (np.loadtxt(os.path.normpath(os.path.join('electricity_data', 'forecast_load_increment_dataset.csv')), delimiter=',')).T
    FORECAST_RENEWABLE_INCREMENTS_NETWORK = (np.loadtxt(os.path.normpath(os.path.join('electricity_data', 'forecast_renewable_increment_dataset.csv')), delimiter=',')).T

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
    file_path = os.path.normpath(os.path.join(current_folder, '..', 'electricity_data', 'initial_dispatchable_power.csv'))
    INITIAL_DISPATCHABLE_POWER = np.loadtxt(file_path, delimiter=',')
    INITIAL_DISPATCHABLE_POWER = (np.atleast_2d(INITIAL_DISPATCHABLE_POWER).T)

    INITIAL_DISPATCHABLE_POWER = INITIAL_DISPATCHABLE_POWER.reshape(-1)

    return MEASURED_LOAD, MEASURED_RENEWABLE, MEASURED_LOAD_INCREMENTS, MEASURED_RENEWABLE_INCREMENTS, FORECAST_LOAD_INCREMENTS, FORECAST_RENEWABLE_INCREMENTS, INITIAL_DISPATCHABLE_POWER, dispatchable_capacities