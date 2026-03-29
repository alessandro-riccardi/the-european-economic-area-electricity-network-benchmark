import numpy as np
import gurobipy as gp
import time as tm


def create_empty_list(N):
    return [[] for _ in range(N)]



def control_simulation_linear_centralized_mpc(simulation_data):

    LIST_ATOMIC_AGENTS = simulation_data["atomic_agents"]
    Control_Agents = simulation_data["Control_Agents"]
    Augmented_Control_Agents = simulation_data["Augmented_Control_Agents"]
    NUM_STATES = simulation_data["NUM_STATES"]
    NUM_INPUTS = simulation_data["NUM_INPUTS"]

    NUMBER_ATOMIC_AGENTS = len(LIST_ATOMIC_AGENTS)
    NUMBER_CONTROL_AGENTS = len(Control_Agents)

    SIMULATION_HORIZON = simulation_data["simulation_horizon"]
    PREDICTION_HORIZON = simulation_data["prediction_horizon"]

    Control_Agents_Matrices = simulation_data["Control_Agents_Matrices"]
    Control_Agents_Optimization_Matrices = simulation_data["Control_Agents_Optimization_Matrices"]
    Reference_Signal = simulation_data["Reference_Signal"]

    LOWER_BOUNDS_INPUT = simulation_data["lower_bounds_inputs"]
    UPPER_BOUNDS_INPUT = simulation_data["upper_bounds_inputs"]
    LOWER_BOUNDS_STATE = simulation_data["lower_bounds_states"]
    UPPER_BOUNDS_STATE = simulation_data["upper_bounds_states"]


    MEASURED_LOAD_INCREMENTS = simulation_data["MEASURED_LOAD_INCREMENTS"]
    MEASURED_RENEWABLE_INCREMENTS = simulation_data["MEASURED_RENEWABLE_INCREMENTS"]
    FORECAST_LOAD_INCREMENTS = simulation_data["FORECAST_LOAD_INCREMENTS"]
    FORECAST_RENEWABLE_INCREMENTS = simulation_data["FORECAST_RENEWABLE_INCREMENTS"]

    EEA_ENB = simulation_data["EEA_ENB"]



    x_evolution = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+1))
    u_evolution = np.zeros((NUM_INPUTS*NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+1))
    w_evolution = np.zeros((2*NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+1))
    w_measured = np.zeros((2*NUMBER_ATOMIC_AGENTS,SIMULATION_HORIZON+1))

    #  Construction of the external signal
    for k in range(0,SIMULATION_HORIZON+1):
        for i in range(0,NUMBER_ATOMIC_AGENTS):
            w_measured[i*2:(i+1)*2,k] = np.array([MEASURED_LOAD_INCREMENTS[i,k],MEASURED_RENEWABLE_INCREMENTS[i,k]])
            if k == 0:
                w_evolution[i*2:(i+1)*2,k] = np.array([MEASURED_LOAD_INCREMENTS[i,k],MEASURED_RENEWABLE_INCREMENTS[i,k]])
            else:
                w_evolution[i*2:(i+1)*2,k] = np.array([FORECAST_LOAD_INCREMENTS[i,k],FORECAST_RENEWABLE_INCREMENTS[i,k]])

    Total_Core_Seconds = 0
    Core_Seconds = create_empty_list(SIMULATION_HORIZON)
    max_number_of_iterations = 1

    # residual_evolution = np.zeros((max_number_of_iterations))

    for i in range(0, SIMULATION_HORIZON):
        Core_Seconds[i] = np.zeros((NUMBER_CONTROL_AGENTS,max_number_of_iterations))


    Simulation_Start_Time_Holder = tm.time()
    Simulation_Timer_Start = tm.time()
    # Simulation 

    for k in range(0,SIMULATION_HORIZON):
        
        print("TIME STEP ", k)
      
        
        Core_Seconds_Control_Agent = np.zeros(NUMBER_CONTROL_AGENTS)

        # Initialize optimization problem
        gurobi_model = gp.Model("CMPC")

        # Optimization Matrices
        M_Optimization = Control_Agents_Optimization_Matrices[0][0].copy()
        C_Optimization = Control_Agents_Optimization_Matrices[0][1].copy()
        D_Optimization = Control_Agents_Optimization_Matrices[0][5].copy()
        Q_Optimization = Control_Agents_Optimization_Matrices[0][2].copy()
        R_Optimization = Control_Agents_Optimization_Matrices[0][3].copy() 

        H_Optimization = (np.transpose(C_Optimization) @ Q_Optimization @ C_Optimization) + R_Optimization

        # Constrcut bounds vectors
        Lower_Bounds_u = np.zeros((NUM_INPUTS*NUMBER_ATOMIC_AGENTS*PREDICTION_HORIZON,1))
        Upper_Bounds_u = np.zeros((NUM_INPUTS*NUMBER_ATOMIC_AGENTS*PREDICTION_HORIZON,1))


        Global_Idx_1 = 0
        for j in range(0,PREDICTION_HORIZON):
            for i in range(0,NUMBER_ATOMIC_AGENTS):

                Lower_Bounds_u[Global_Idx_1,0] = LOWER_BOUNDS_INPUT[0,i]
                Upper_Bounds_u[Global_Idx_1,0] = UPPER_BOUNDS_INPUT[0,i]
                Lower_Bounds_u[Global_Idx_1+1,0] = LOWER_BOUNDS_INPUT[1,i]
                Upper_Bounds_u[Global_Idx_1+1,0] = UPPER_BOUNDS_INPUT[1,i]
                Lower_Bounds_u[Global_Idx_1+2,0] = LOWER_BOUNDS_INPUT[2,i]
                Upper_Bounds_u[Global_Idx_1+2,0] = UPPER_BOUNDS_INPUT[2,i]
                Global_Idx_1 += NUM_INPUTS

        # for j in range(0,PREDICTION_HORIZON):
        #     Lower_Bounds_u[j*NUM_INPUTS*NUMBER_ATOMIC_AGENTS:(j+1)*NUM_INPUTS*NUMBER_ATOMIC_AGENTS] = LOWER_BOUNDS_INPUT
        #     Upper_Bounds_u[j*NUM_INPUTS*NUMBER_ATOMIC_AGENTS:(j+1)*NUM_INPUTS*NUMBER_ATOMIC_AGENTS] = UPPER_BOUNDS_INPUT


        # Optimization Variables
        u_tilde_k = gurobi_model.addMVar((NUM_INPUTS*NUMBER_ATOMIC_AGENTS*PREDICTION_HORIZON, 1), lb = Lower_Bounds_u, ub = Upper_Bounds_u)

        x_k_l = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,1))
        reference_k_l = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS*PREDICTION_HORIZON,1))
        external_signals_k_l = np.zeros((2*NUMBER_ATOMIC_AGENTS*PREDICTION_HORIZON,1))

        Global_Idx = 0
        for j in range(0,PREDICTION_HORIZON):
            for i in range(0,NUMBER_ATOMIC_AGENTS):
                reference_k_l[Global_Idx:Global_Idx+5,0] = Reference_Signal[i*5:(i+1)*5,k+j].copy()
                Global_Idx += NUM_STATES


        Global_Idx = 0
        # Collecting the initial state from the global state evolution vector
        for i in range(0,NUMBER_ATOMIC_AGENTS):
            x_k_l[Global_Idx*NUM_STATES:(Global_Idx+1)*NUM_STATES,0] = x_evolution[i*NUM_STATES:(i+1)*NUM_STATES,k].copy()    
            Global_Idx += 1

        Global_Idx = 0
        for j in range(0, PREDICTION_HORIZON):
            for i in range(0,NUMBER_ATOMIC_AGENTS):
                
                if j == 0:
                    external_signals_k_l[Global_Idx*2:(Global_Idx+1)*2,0] = np.array([MEASURED_LOAD_INCREMENTS[i,k+j],
                                                                                    MEASURED_RENEWABLE_INCREMENTS[i,k+j]])
                    Global_Idx += 1
                else:
                    external_signals_k_l[Global_Idx*2:(Global_Idx+1)*2,0] = np.array([FORECAST_LOAD_INCREMENTS[i,k+j],
                                                                                    FORECAST_RENEWABLE_INCREMENTS[i,k+j]])
                    Global_Idx += 1


        x_tilde_k = M_Optimization @ x_k_l + C_Optimization @ u_tilde_k + D_Optimization @ external_signals_k_l
        
        Global_Idx = 0
        for j in range(0,PREDICTION_HORIZON):
            for i in range(0,NUMBER_ATOMIC_AGENTS):
                         
                gurobi_model.addConstr(x_tilde_k[Global_Idx] <= UPPER_BOUNDS_STATE[0,i])
                gurobi_model.addConstr(x_tilde_k[Global_Idx] >= LOWER_BOUNDS_STATE[0,i])

                gurobi_model.addConstr(x_tilde_k[Global_Idx+1] <= UPPER_BOUNDS_STATE[1,i])
                gurobi_model.addConstr(x_tilde_k[Global_Idx+1] >= LOWER_BOUNDS_STATE[1,i])

                gurobi_model.addConstr(x_tilde_k[Global_Idx+2] <= UPPER_BOUNDS_STATE[2,i])
                gurobi_model.addConstr(x_tilde_k[Global_Idx+2] >= 0)

                gurobi_model.addConstr(x_tilde_k[Global_Idx+4] <= UPPER_BOUNDS_STATE[4,i])
                gurobi_model.addConstr(x_tilde_k[Global_Idx+4] >= 0)

                Global_Idx += NUM_STATES

        # Cost function
        Stage_Cost = (u_tilde_k.T @ H_Optimization @ u_tilde_k) + 2*(np.transpose(x_k_l) @ np.transpose(M_Optimization) - reference_k_l.T) @ Q_Optimization @ C_Optimization @ u_tilde_k  + 2*(np.transpose(external_signals_k_l) @ np.transpose(D_Optimization)) @ Q_Optimization @ C_Optimization @ u_tilde_k 


        # Optimization Options
        gurobi_model.setObjective(Stage_Cost, gp.GRB.MINIMIZE) 
        gurobi_model.Params.LogToConsole = 0
        # gurobi_model.Params.FeasibilityTol = 1e-9
        # gurobi_model.Params.NumericFocus = 1
        
        # Local Optimization
        gurobi_model.optimize()

        # Retrieving the optimal solution
        u_local_k = np.zeros((NUM_INPUTS*NUMBER_ATOMIC_AGENTS, PREDICTION_HORIZON))

        var_idx = 0
        for i in range(0,NUM_INPUTS*NUMBER_ATOMIC_AGENTS):
            u_evolution[i,k] = gurobi_model.getVars()[var_idx].x
            var_idx += 1

        # Apply control action and update state evolution
        

        x_evolution[:,k+1] =  EEA_ENB.step(u_evolution[:,k], w_evolution[:,k])
        w_evolution[:,k+1] = w_measured[:,k+1].copy()

        print("Mean evolution error norm = ", (np.linalg.norm(Reference_Signal[:,k] - x_evolution[:,k]))/NUMBER_ATOMIC_AGENTS)
        Simulation_Timer_End = tm.time() - Simulation_Timer_Start
        print("Enlapsed time:", round(Simulation_Timer_End,2), "[s]")
        print("Expected time to finish:", round(((Simulation_Timer_End*SIMULATION_HORIZON)/(k+1)) - Simulation_Timer_End, 2), "[s]")

    Simulation_Total_Time = tm.time() - Simulation_Start_Time_Holder
    print("Simulation = ", Simulation_Total_Time, " [s]")

    return x_evolution, u_evolution, w_evolution



def control_simulation(simulation_data):

    model = simulation_data["model"]
    control_strategy = simulation_data["control_strategy"]

    if model == 'linear' and control_strategy == 'Centralized_MPC':
        return control_simulation_linear_centralized_mpc(simulation_data)
    else:
        # Here add the distributed MPC control simulation for the linear model when the function is implemented, and the other combinations of model and control strategy when they are implemented
        raise NotImplementedError(f"Control simulation for model '{model}' and control strategy '{control_strategy}' is not implemented yet.")
    