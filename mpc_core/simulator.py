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




    residual_norm = np.zeros((NUMBER_CONTROL_AGENTS))
    Total_Core_Seconds = 0
    Core_Seconds = create_empty_list(SIMULATION_HORIZON)
    # max_number_of_iterations = 100
    max_number_of_iterations = 1

    residual_evolution = np.zeros((max_number_of_iterations))

    for i in range(0, SIMULATION_HORIZON):
        Core_Seconds[i] = np.zeros((NUMBER_CONTROL_AGENTS,max_number_of_iterations))

    rho = 0.1
    epsilon_convergence = 0.001

    u_local = create_empty_list(NUMBER_CONTROL_AGENTS)
    x_local = create_empty_list(NUMBER_CONTROL_AGENTS)

    u_avarage_local = np.zeros((NUM_INPUTS*NUMBER_ATOMIC_AGENTS, PREDICTION_HORIZON))
    x_avarage_local = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS, PREDICTION_HORIZON))

    consensus_variable = create_empty_list(NUMBER_CONTROL_AGENTS)
    avarage_variable = create_empty_list(NUMBER_CONTROL_AGENTS)
    avarage_variable_old = create_empty_list(NUMBER_CONTROL_AGENTS)
    gamma = create_empty_list(NUMBER_CONTROL_AGENTS)

    for l in range(0,NUMBER_CONTROL_AGENTS):
        number_of_agents_l = len(Augmented_Control_Agents[l])
        
        avarage_variable[l] = np.zeros(((NUM_STATES+NUM_INPUTS)*number_of_agents_l*PREDICTION_HORIZON,1))
        consensus_variable[l] = np.zeros(((NUM_STATES+NUM_INPUTS)*number_of_agents_l*PREDICTION_HORIZON,1))
        gamma[l] = np.zeros(((NUM_STATES+NUM_INPUTS)*number_of_agents_l*PREDICTION_HORIZON,1))

    Simulation_Start_Time_Holder = tm.time()
    Simulation_Timer_Start = tm.time()
    # Simulation 

    for k in range(0,SIMULATION_HORIZON):
        
        print("TIME STEP ", k)
        number_of_iterations = 0
        norm_codition_1 = False
        norm_codition_2 = False
        norm_codition_3 = False
        
        Core_Seconds_Control_Agent = np.zeros(NUMBER_CONTROL_AGENTS)

        while (number_of_iterations < max_number_of_iterations) and (norm_codition_1 == False) and (norm_codition_2 == False):

            print("Local iteration ", number_of_iterations + 1)

            for l in range(0,len(Augmented_Control_Agents)):
                Start_Time_Holder = tm.time()
                number_of_agents_l = len(Augmented_Control_Agents[l])
                
                #  Avarage variable store for norm evaluation
                avarage_variable_old[l] = avarage_variable[l].copy()

                # Local optimization matrices
                M_Optimization = Control_Agents_Optimization_Matrices[l][0].copy()
                C_Optimization = Control_Agents_Optimization_Matrices[l][1].copy()
                # Cu_Optimization = Control_Agents_Optimization_Matrices[l][1].copy()
                # Cz_Optimization = Control_Agents_Optimization_Matrices[l][4].copy()
                D_Optimization = Control_Agents_Optimization_Matrices[l][5].copy()
                Q_Optimization = Control_Agents_Optimization_Matrices[l][2].copy()
                R_Optimization = Control_Agents_Optimization_Matrices[l][3].copy() 
                # R_Optimization_PWA = Control_Agents_Optimization_Matrices[l][7].copy() 

                #  Model initialization
                gurobi_model = gp.Model("MPC_Local")

                #  State at k and reference for the agent
                x_k_l = np.zeros((NUM_STATES*number_of_agents_l,1))
                reference_k_l = np.zeros((NUM_STATES*number_of_agents_l*PREDICTION_HORIZON,1))
                external_signals_k_l = np.zeros((2*number_of_agents_l*PREDICTION_HORIZON,1))

                Global_Idx = 0
                for j in range(0,PREDICTION_HORIZON):
                    for i in range(0,NUMBER_ATOMIC_AGENTS):
                        if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
                            reference_k_l[Global_Idx:Global_Idx+5,0] = Reference_Signal[i*5:(i+1)*5,k+j].copy()
                            Global_Idx += 5

                # d_l = np.zeros((2*number_of_agents_l,PREDICTION_HORIZON))

                Global_Idx = 0
                
                # Collecting the initial state from the global state evolution vector
                for i in range(0,NUMBER_ATOMIC_AGENTS):
                    if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
                        x_k_l[Global_Idx*NUM_STATES:(Global_Idx+1)*NUM_STATES,0] = x_evolution[i*NUM_STATES:(i+1)*NUM_STATES,k].copy()
                        
                        Global_Idx += 1

                # Collecting the external signals for optimization signal and external signal for dynamics
                # Global_Idx = 0
                # for j in range(0, PREDICTION_HORIZON):
                #     for i in range(0,NUMBER_ATOMIC_AGENTS):
                #         if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
                #             external_signals_k_l[Global_Idx*2:(Global_Idx+1)*2,0] = np.array([MEASURED_LOAD_INCREMENTS[i,k+j],
                #                                                                               MEASURED_RENEWABLE_INCREMENTS[i,k+j]])
                #             Global_Idx += 1
                # distinguishiong between measured and forecast
                Global_Idx = 0
                for j in range(0, PREDICTION_HORIZON):
                    for i in range(0,NUMBER_ATOMIC_AGENTS):
                        if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
                            if j == 0:
                                external_signals_k_l[Global_Idx*2:(Global_Idx+1)*2,0] = np.array([MEASURED_LOAD_INCREMENTS[i,k+j],
                                                                                                MEASURED_RENEWABLE_INCREMENTS[i,k+j]])
                                Global_Idx += 1
                            else:
                                external_signals_k_l[Global_Idx*2:(Global_Idx+1)*2,0] = np.array([FORECAST_LOAD_INCREMENTS[i,k+j],
                                                                                                FORECAST_RENEWABLE_INCREMENTS[i,k+j]])
                                Global_Idx += 1
                
                # Input bounds contruction
                Lower_Bounds_u = np.zeros((NUM_INPUTS*number_of_agents_l*PREDICTION_HORIZON,1))
                Upper_Bounds_u = np.zeros((NUM_INPUTS*number_of_agents_l*PREDICTION_HORIZON,1))
                # Lower_Bounds_z = np.zeros((8*number_of_agents_l*PREDICTION_HORIZON,1))
                # Upper_Bounds_z = np.zeros((8*number_of_agents_l*PREDICTION_HORIZON,1))

                # Lower_Bounds_u_PWA = np.zeros((NUM_INPUTS*number_of_agents_l*PREDICTION_HORIZON,1))
                # Upper_Bounds_u_PWA = np.zeros((NUM_INPUTS*number_of_agents_l*PREDICTION_HORIZON,1))
                
                # Construction of bounds for the input over the horizon from indivifual bounds
                Global_Idx_1 = 0
                # Global_Idx_2 = 0
                # Global_Idx_3 = 0
                for j in range(0,PREDICTION_HORIZON):
                    for i in range(0,NUMBER_ATOMIC_AGENTS):
                        if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:

                            Lower_Bounds_u[Global_Idx_1,0] = LOWER_BOUNDS_INPUT[0,i]
                            Upper_Bounds_u[Global_Idx_1,0] = UPPER_BOUNDS_INPUT[0,i]
                            Lower_Bounds_u[Global_Idx_1+1,0] = LOWER_BOUNDS_INPUT[1,i]
                            Upper_Bounds_u[Global_Idx_1+1,0] = UPPER_BOUNDS_INPUT[1,i]
                            Lower_Bounds_u[Global_Idx_1+2,0] = LOWER_BOUNDS_INPUT[2,i]
                            Upper_Bounds_u[Global_Idx_1+2,0] = UPPER_BOUNDS_INPUT[2,i]

                            # Lower_Bounds_u_PWA[Global_Idx_3,0] = LOWER_BOUNDS_INPUT[0,i]
                            # Upper_Bounds_u_PWA[Global_Idx_3,0] = UPPER_BOUNDS_INPUT[0,i]
                            # Lower_Bounds_u_PWA[Global_Idx_3+1,0] = LOWER_BOUNDS_INPUT[1,i]
                            # Upper_Bounds_u_PWA[Global_Idx_3+1,0] = UPPER_BOUNDS_INPUT[1,i]
                            # for m in range(0,8):
                            #     Lower_Bounds_z[Global_Idx_2 + m,0] = LOWER_BOUNDS_INPUT[1,i]
                            #     Upper_Bounds_z[Global_Idx_2 + m,0] = UPPER_BOUNDS_INPUT[1,i]
                            
                
                            Global_Idx_1 += 3
                            # Global_Idx_2 += 8
                            # Global_Idx_3 += 2
    
                # Variables
                u_tilde_k = gurobi_model.addMVar((NUM_INPUTS*number_of_agents_l*PREDICTION_HORIZON, 1), lb = Lower_Bounds_u, ub = Upper_Bounds_u)
                # u_tilde_k_Pdis = gurobi_model.addMVar((number_of_agents_l*PREDICTION_HORIZON, 1), lb = Lower_Bounds_u, ub = Upper_Bounds_u)
                # u_tilde_k_PESS = gurobi_model.addMVar((number_of_agents_l*PREDICTION_HORIZON, 1), lb = Lower_Bounds_u, ub = Upper_Bounds_u)
                # z_tilde_k = gurobi_model.addMVar((8*number_of_agents_l*PREDICTION_HORIZON, 1), lb = Lower_Bounds_z, ub = Upper_Bounds_z)
                # d_tilde_k = gurobi_model.addMVar((8*number_of_agents_l*PREDICTION_HORIZON, 1), vtype=gp.GRB.BINARY)

                # for i in range(0,number_of_agents_l*PREDICTION_HORIZON):
                #     gurobi_model.addConstr(u_tilde_k_Pdis[i] == u_tilde_k[2*i])
                #     gurobi_model.addConstr(u_tilde_k_PESS[i] == u_tilde_k[(2*i)+1])



                # State variable update as a function of optimization variables to implement explicit formulation
                x_tilde_k = M_Optimization @ x_k_l + C_Optimization @ u_tilde_k + D_Optimization @ external_signals_k_l

                # Eta = np.array([0.9, 0.7, 0.5, 0.3, 1/0.9, 1/0.7, 1/0.5, 1/0.3])

                # MARK: Blocking
                #  For N = 30
                # gurobi_model.addConstr(u_tilde_k[2*number_of_agents_l*int(2*PREDICTION_HORIZON/6):2*number_of_agents_l*int(3*PREDICTION_HORIZON/6)] == u_tilde_k[2*number_of_agents_l*int(3*PREDICTION_HORIZON/6):2*number_of_agents_l*int(4*PREDICTION_HORIZON/6)])
                # gurobi_model.addConstr(u_tilde_k[2*number_of_agents_l*int(4*PREDICTION_HORIZON/6):2*number_of_agents_l*int(5*PREDICTION_HORIZON/6)] == u_tilde_k[2*number_of_agents_l*int(5*PREDICTION_HORIZON/6):2*number_of_agents_l*int(6*PREDICTION_HORIZON/6)])
                
                # Constraints on the state
                Global_Idx = 0
                for j in range(0,PREDICTION_HORIZON):
                    for i in range(0,NUMBER_ATOMIC_AGENTS):
                        if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
                            
                            gurobi_model.addConstr(x_tilde_k[Global_Idx] <= UPPER_BOUNDS_STATE[0,i])
                            gurobi_model.addConstr(x_tilde_k[Global_Idx] >= LOWER_BOUNDS_STATE[0,i])

                            gurobi_model.addConstr(x_tilde_k[Global_Idx+1] <= UPPER_BOUNDS_STATE[1,i])
                            gurobi_model.addConstr(x_tilde_k[Global_Idx+1] >= LOWER_BOUNDS_STATE[1,i])

                            gurobi_model.addConstr(x_tilde_k[Global_Idx+2] <= UPPER_BOUNDS_STATE[2,i])
                            gurobi_model.addConstr(x_tilde_k[Global_Idx+2] >= 0)

                            gurobi_model.addConstr(x_tilde_k[Global_Idx+4] <= UPPER_BOUNDS_STATE[4,i])
                            gurobi_model.addConstr(x_tilde_k[Global_Idx+4] >= 0)

                            Global_Idx += 5

                # Constraints on delta
                #  Only one delta = 1 for each agent, at each time step
                # Global_Idx_3 = 0
                # for j in range(0,PREDICTION_HORIZON):
                #     Sum_Deltas = 0
                #     for m in range(0,8):
                #         Sum_Deltas = Sum_Deltas + d_tilde_k[Global_Idx_3 + m]
                #     gurobi_model.addConstr(Sum_Deltas == 1)
                #     Global_Idx_3 += 8

                # Constraints on auxiliary variables
                # Global_Idx_1 = 0
                # Global_Idx_2 = 0
                # for j in range(0,PREDICTION_HORIZON):
                #     for i in range(0,NUMBER_ATOMIC_AGENTS):
                #         if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:

                #             # Auxiliary variables bounds
                #             P_ESS_i_MAX = UPPER_BOUNDS_INPUT[1,i]
                #             P_ESS_i_min = LOWER_BOUNDS_INPUT[1,i]

                #             # PESS Construction for bounds
                #             PESS = 0
                #             for m in range(0,8):
                #                 PESS = PESS + (z_tilde_k[Global_Idx_1 + m]/Eta[m])


                #             # Contraints connection

                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1])
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+1] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+1])
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+2] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+2])
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+3] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+3])
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+4] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+4])
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+5] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+5])
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+6] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+6])
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+7] == u_tilde_k_PESS[Global_Idx_2]*d_tilde_k[Global_Idx_1+7])

                #             # Mode 0
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1]))
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1]))
                #             #  Mode 1
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+1] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+1]))
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+1] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+1]))
                #             #  Mode 2
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+2] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+2]))
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+2] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+2]))
                #             #  Mode 3
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+3] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+3]))
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+3] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+3]))
                #             #  Mode 4
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+4] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+4]))
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+4] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+4]))
                #             #  Mode 5
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+5] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+5]))
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+5] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+5]))
                #             #  Mode 6
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+6] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+6]))
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+6] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+6]))
                #             #  Mode 7
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+7] <= u_tilde_k_PESS[Global_Idx_2] - (-P_ESS_i_MAX)*(1 - d_tilde_k[Global_Idx_1+7]))
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+7] >= u_tilde_k_PESS[Global_Idx_2] - P_ESS_i_MAX*(1 - d_tilde_k[Global_Idx_1+7]))

                #             #  Old contraints
                #             # Mode 0
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1] <= (P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1] - EPSILON)
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1] >= 0 * d_tilde_k[Global_Idx_1])

                #             # Mode 1
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+1] <= 2*(P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1+1] - EPSILON) 
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+1] >= (P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+1])

                #             # Mode 2
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+2] <= 3*(P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1+2] - EPSILON)
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+2] >= 2*(P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+2])

                #             # Mode 3
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+3] <= 4*(P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1+3])
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+3] >= 3*(P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+3])

                #             # Mode 4
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+4] <= 0 * d_tilde_k[Global_Idx_1+4] - EPSILON)
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+4] >= -(P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+4] + EPSILON)

                #             # Mode 5
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+5] <= -(P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1+5])
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+5] >= -2*(P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+5] + EPSILON)

                #             # Mode 6
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+6] <= -2*(P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1+6])
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+6] >= -3*(P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+6] + EPSILON)

                #             # Mode 7
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+7] <= -3*(P_ESS_i_MAX/4) * d_tilde_k[Global_Idx_1+7])
                #             gurobi_model.addConstr(z_tilde_k[Global_Idx_1+7] >= -4*(P_ESS_i_MAX/4)  * d_tilde_k[Global_Idx_1+7])

                #             Global_Idx_1 += 8
                #             Global_Idx_2 += 1

                # Cost function matrices
                H_Optimization = (np.transpose(C_Optimization) @ Q_Optimization @ C_Optimization) + R_Optimization
                # Hu_Optimization_PWA = (np.transpose(C_Optimization) @ Q_Optimization @ C_Optimization) + R_Optimization_PWA

                # Cost function for the minimization of the auxiliary variables
                # R_Optimization_z = np.zeros((8*number_of_agents_l*PREDICTION_HORIZON,8*number_of_agents_l*PREDICTION_HORIZON))
                # for Idx in range(0, len(R_Optimization_z)):
                #     R_Optimization_z[Idx,Idx] = 1

                # Hz_Optimization =  (np.transpose(Cz_Optimization) @ Q_Optimization @ Cz_Optimization) + R_Optimization_z

                # Cost function 
                # Stage cost including ADMM
                gamma_l = gamma[l].reshape(len(gamma[l]),).copy()
                consensus_variable_l = consensus_variable[l].reshape(len(consensus_variable[l]),).copy()
                avarage_variable_l = avarage_variable[l].reshape(len(avarage_variable[l]),).copy()
                
                # Stage_Cost = (u_tilde_k.T @ H_Optimization @ u_tilde_k) + 2*(np.transpose(x_k_l) @ np.transpose(M_Optimization) - reference_k_l.T) @ Q_Optimization @ C_Optimization @ u_tilde_k  + 2*(np.transpose(external_signals_k_l) @ np.transpose(D_Optimization)) @ Q_Optimization @ C_Optimization @ u_tilde_k + np.transpose(gamma_l)@(consensus_variable_l - avarage_variable_l) + (rho/2)*np.transpose(consensus_variable_l - avarage_variable_l)@(consensus_variable_l - avarage_variable_l)
                Stage_Cost = (u_tilde_k.T @ H_Optimization @ u_tilde_k) + 2*(np.transpose(x_k_l) @ np.transpose(M_Optimization) - reference_k_l.T) @ Q_Optimization @ C_Optimization @ u_tilde_k  + 2*(np.transpose(external_signals_k_l) @ np.transpose(D_Optimization)) @ Q_Optimization @ C_Optimization @ u_tilde_k 
                

                # Options
                gurobi_model.setObjective(Stage_Cost, gp.GRB.MINIMIZE) 
                gurobi_model.Params.LogToConsole = 0
                # gurobi_model.Params.FeasibilityTol = 1e-9
                # gurobi_model.Params.NumericFocus = 1
                
                # Local Optimization
                gurobi_model.optimize()

                # Results
                # Local variables
                u_local_k = np.zeros((NUM_INPUTS*number_of_agents_l, PREDICTION_HORIZON))
                PDisp_local_k = np.zeros((number_of_agents_l, PREDICTION_HORIZON))
                PESS_local_k = np.zeros((2*number_of_agents_l, PREDICTION_HORIZON))
                x_local_k = np.zeros((NUM_STATES*number_of_agents_l, PREDICTION_HORIZON+1))
                # z_local_k = np.zeros((8*number_of_agents_l, PREDICTION_HORIZON))
                d_local_k = np.zeros((2*number_of_agents_l,PREDICTION_HORIZON))

                var_idx = 0
                for j in range(0, PREDICTION_HORIZON):
                    for i in range(0,NUM_INPUTS*number_of_agents_l):
                        u_local_k[i,j] = gurobi_model.getVars()[var_idx].x
                        var_idx += 1
                # var_idx = 0
                # for j in range(0, PREDICTION_HORIZON):
                #     for i in range(0,number_of_agents_l):
                #         PDisp_local_k[i,j] = gurobi_model.getVars()[var_idx].x
                #         var_idx += 1
                # for j in range(0, PREDICTION_HORIZON):
                #     for i in range(0,number_of_agents_l):
                #         PESS_local_k[i,j] = gurobi_model.getVars()[var_idx].x
                #         var_idx += 1
                # for j in range(0, PREDICTION_HORIZON):
                #     for i in range(0,8*number_of_agents_l):
                #         z_local_k[i,j] = gurobi_model.getVars()[var_idx].x
                #         var_idx += 1

                # Local initial state
                Global_Idx = 0
                for i in range(0,NUMBER_ATOMIC_AGENTS):
                    if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
                        x_local_k[Global_Idx:Global_Idx+NUM_STATES,0] = x_evolution[i:i+NUM_STATES,k]
                        Global_Idx += NUM_STATES

                # THIS IS WRONG, NOT OVER THE PREDICTION HORIZON
                Global_Idx = 0
                for i in range(0, NUMBER_ATOMIC_AGENTS):
                    if LIST_ATOMIC_AGENTS[i] in Augmented_Control_Agents[l]:
                        # d_local_k[Global_Idx:Global_Idx +2,:] = np.array([MEASURED_LOAD_INCREMENTS[i,k:k+PREDICTION_HORIZON],
                        #                                                   MEASURED_RENEWABLE_INCREMENTS[i,k:k+PREDICTION_HORIZON]])
                        d_local_k[Global_Idx:Global_Idx +2,0] = np.array([MEASURED_LOAD_INCREMENTS[i,k],
                                                                        MEASURED_RENEWABLE_INCREMENTS[i,k]])
                        d_local_k[Global_Idx:Global_Idx +2,1:1+PREDICTION_HORIZON] = np.array([MEASURED_LOAD_INCREMENTS[i,k+1:k+PREDICTION_HORIZON],
                                                                        MEASURED_RENEWABLE_INCREMENTS[i,k+1:k+PREDICTION_HORIZON]])
                        Global_Idx += 2

                # Local simualtion
                A_Augmented = Control_Agents_Matrices[l][0].copy()
                B_Augmented = Control_Agents_Matrices[l][1].copy()
                # Bz_Augmented = Control_Agents_Matrices[l][4].copy()
                D_Augmented = Control_Agents_Matrices[l][5].copy()

                for k_local in range(0,PREDICTION_HORIZON):
                    x_local_k[:,k_local+1] = A_Augmented @ x_local_k[:,k_local] + B_Augmented @ u_local_k[:,k_local] + D_Augmented @ d_local_k[:,k_local]
                    # x_local_k[:,k_local+1] = A_Augmented @ x_local_k[:,k_local] + B_Augmented @ u_local_k[:,k_local] + D_Augmented @ external_signals_k_l

                u_local[l] = u_local_k.copy()
                x_local[l] = x_local_k[:,1:].copy()

                # Build the consensus variable
                y_consensus = np.zeros((0,0))
                
                for i in range(0,NUM_INPUTS*number_of_agents_l):
                    y_consensus = np.concatenate((y_consensus,u_local_k[i,:]), axis=None)
                for i in range(0,NUM_STATES*number_of_agents_l):
                    y_consensus = np.concatenate((y_consensus,x_local_k[i,1:]), axis=None)

                consensus_variable[l] = y_consensus.T

                # Global input

                for i in range(0,NUMBER_ATOMIC_AGENTS):
                    Agent_Index = LIST_ATOMIC_AGENTS[i]
                    for j in range(0,len(Control_Agents[l])):
                        if Agent_Index == Control_Agents[l][j]:
                            Agent_Index_Augmented = Augmented_Control_Agents[l].index(Agent_Index)
                            # print("Agent: ", i)
                            # print("Selection: ", Augmented_Control_Agents[l][Agent_Index])
                            u_evolution[i*NUM_INPUTS:(i+1)*NUM_INPUTS,k] = u_local_k[Agent_Index_Augmented*NUM_INPUTS:(Agent_Index_Augmented+1)*NUM_INPUTS,0].copy()
                
                
                Total_Time_Holder = tm.time() - Start_Time_Holder
                Core_Seconds[k][l,number_of_iterations] = Core_Seconds[k][l,number_of_iterations] + Total_Time_Holder

            # MARK: Consensus Structure

            u_avarage_local = np.zeros((NUM_INPUTS*NUMBER_ATOMIC_AGENTS, PREDICTION_HORIZON))
            x_avarage_local = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS, PREDICTION_HORIZON))
            total_copies_vector = np.zeros((NUMBER_CONTROL_AGENTS))

            for l in range(0,NUMBER_ATOMIC_AGENTS):   
                
                total_copies = 0

                for i in range(0,NUMBER_CONTROL_AGENTS):
                    Start_Time_Holder = tm.time()
                    u_local_k = u_local[i]
                    x_local_k = x_local[i]
                    for j in range(0,len(Augmented_Control_Agents[i])):
                        if l == Augmented_Control_Agents[i][j]:
                            u_avarage_local[l*NUM_INPUTS:(l+1)*NUM_INPUTS,:] = u_avarage_local[l*NUM_INPUTS:(l+1)*NUM_INPUTS,:] + u_local_k[j*NUM_INPUTS:(j+1)*NUM_INPUTS,:]
                            x_avarage_local[l*NUM_STATES:(l+1)*NUM_STATES,:] = x_avarage_local[l*NUM_STATES:(l+1)*NUM_STATES,:] + x_local_k[j*NUM_STATES:(j+1)*NUM_STATES,:]
                            total_copies += 1
                    Total_Time_Holder = tm.time() - Start_Time_Holder
                    Core_Seconds[k][i,number_of_iterations] = Core_Seconds[k][i,number_of_iterations] + Total_Time_Holder
                if total_copies > 0:        
                    u_avarage_local[l*NUM_INPUTS:(l+1)*NUM_INPUTS,:] = u_avarage_local[l*NUM_INPUTS:(l+1)*NUM_INPUTS,:]/total_copies
                    x_avarage_local[l*NUM_STATES:(l+1)*NUM_STATES,:] = x_avarage_local[l*NUM_STATES:(l+1)*NUM_STATES,:]/total_copies
                

            # Computation of the avarage variable for each control agent
            for l in range(0,NUMBER_CONTROL_AGENTS):
                Start_Time_Holder = tm.time()

                number_of_agents_l = len(Augmented_Control_Agents[l])

                y_avarage = np.zeros((0,0))

                for i in range(0,number_of_agents_l):
                    variable_index = LIST_ATOMIC_AGENTS.index(Augmented_Control_Agents[l][i])
                    for Input_Index in range(0,NUM_INPUTS):
                        y_avarage = np.concatenate((y_avarage,u_avarage_local[(variable_index*NUM_INPUTS)+Input_Index,:]), axis=None)
                for i in range(0,number_of_agents_l):
                    variable_index = LIST_ATOMIC_AGENTS.index(Augmented_Control_Agents[l][i])
                    for Input_Index in range(0,NUM_STATES):
                        y_avarage = np.concatenate((y_avarage,x_avarage_local[(variable_index*NUM_STATES)+Input_Index,:]), axis=None)
                
                total_neighbors = 1
                if len(Augmented_Control_Agents[l]) - len(Control_Agents[l]) > 0:
                    total_neighbors = len(Augmented_Control_Agents[l]) - len(Control_Agents[l])
                gamma_l = gamma[l].reshape(len(gamma[l]),).copy()
                avarage_variable[l] = y_avarage.T + ((1/(rho*total_neighbors))*gamma_l )
                Total_Time_Holder = tm.time() - Start_Time_Holder
                Core_Seconds[k][l,number_of_iterations] = Core_Seconds[k][l,number_of_iterations] + Total_Time_Holder
                


            #  Gamma Update
            for l in range(0,len(Augmented_Control_Agents)):
                Start_Time_Holder = tm.time()
                y_consensus = consensus_variable[l].reshape(len(consensus_variable[l]),).copy()
                y_avarage = avarage_variable[l].reshape(len(avarage_variable[l]),).copy()
                gamma_l = gamma[l].reshape(len(gamma[l]),).copy()
                gamma[l] = gamma_l + rho*(y_consensus - y_avarage)
                Total_Time_Holder = tm.time() - Start_Time_Holder
                Core_Seconds[k][l,number_of_iterations] = Core_Seconds[k][l,number_of_iterations] + Total_Time_Holder

            # Check norm conditions
            norm_codition_1 = True
            norm_codition_2 = True
            norm_codition_3 = True

            max_norm_error_1 = float('-inf')
            max_norm_error_2 = float('-inf')

            for l in range(0,NUMBER_CONTROL_AGENTS):
                Start_Time_Holder = tm.time()

                y_consensus = consensus_variable[l].copy()
                y_avarage = avarage_variable[l].copy()
                y_avarage_old = avarage_variable_old[l].copy()

                gamma_l = gamma[l].copy()
                alpha_l = np.linalg.norm(y_consensus - y_avarage, ord = 2)
                beta_l = rho*np.linalg.norm(y_avarage - y_avarage_old, ord = 2)

                epsilon_1 = 0.001*max(np.linalg.norm(y_consensus, ord = 2), np.linalg.norm(y_avarage, ord = 2))
                epsilon_2 = 0.001*np.linalg.norm(gamma_l, ord = 2)
                
                if alpha_l > epsilon_1:
                    norm_codition_1 = False
                if alpha_l - epsilon_1> max_norm_error_1:
                    max_norm_error_1 = alpha_l - epsilon_1
                
                if beta_l > epsilon_2:
                    norm_codition_2 = False
                if beta_l - epsilon_2> max_norm_error_2:
                    max_norm_error_2 = beta_l - epsilon_2
                Total_Time_Holder = tm.time() - Start_Time_Holder
                Core_Seconds[k][l,number_of_iterations] = Core_Seconds[k][l,number_of_iterations] + Total_Time_Holder

            for l in range(0,NUMBER_CONTROL_AGENTS):
                gamma_l = gamma[l].reshape(len(gamma[l]),).copy()
                consensus_variable_l = consensus_variable[l].reshape(len(consensus_variable[l]),).copy()
                avarage_variable_l = avarage_variable[l].reshape(len(avarage_variable[l]),).copy()
                residual_norm[l] = np.linalg.norm(consensus_variable_l - avarage_variable_l, ord=2)
                
            # norm_codition_1 = True
            for l in range(0,NUMBER_CONTROL_AGENTS):
                if residual_norm[l] > epsilon_convergence:
                    norm_codition_3 = False

            # if (max_norm_error_1 < 0) and (max_norm_error_2 < 0):
            #     norm_codition_2 = True 


            residual_evolution[number_of_iterations] = residual_evolution[number_of_iterations] + np.max(residual_norm)
        
            #  Update number of iteration
            number_of_iterations += 1
            #  Print exit conditions
            if norm_codition_1 == True:
                print("---------------> Exit for norm condition 1. Max norm:", np.max(residual_norm))
            elif norm_codition_2 == True:
                print("---------------> Exit for norm condition 2. Max norm:", np.max(residual_norm))
            elif norm_codition_3 == True:
                print("---------------> Exit for norm condition 3. Max norm:", np.max(residual_norm))
            elif number_of_iterations >= max_number_of_iterations:
                print("---------------> Exit for max iterations", np.max(residual_norm))
            else:
                print("---------------> Reiteration. Max norm:", np.max(residual_norm))

            
            print("Max deviation condition 1: ", max_norm_error_1)
            print("Max deviation condition 2: ", max_norm_error_2)
            # #  Print exit conditions
            # if norm_codition_1 == True:
            #     print("---------------> Exit for norm condition 1. Max norm:", np.max(residual_norm))
            # elif norm_codition_2 == True:
            #     print("---------------> Exit for norm condition 2. Max norm:", np.max(residual_norm))
            # elif number_of_iterations >= max_number_of_iterations:
            #     print("---------------> Exit for max iterations")
            # else:
            #     print("---------------> Reiteration. Max norm:", np.max(residual_norm))
            
            # print("Max deviation condition 1: ", max_norm_error_1)
            # print("Max deviation condition 2: ", max_norm_error_2)
        
        # State update using PWA dynamics and global solution
        print("Mean evolution error norm = ", (np.linalg.norm(Reference_Signal[:,k] - x_evolution[:,k]))/NUMBER_ATOMIC_AGENTS)
        
        
        # NUMBER_ATOMIC_AGENTS = PARAMETERS_LIST[0]
        # UPPER_BOUNDS_STATE = PARAMETERS_LIST[8]
        # TAU = PARAMETERS_LIST[13]

        # A_Dynamics = PARAMETERS_LIST[3].copy()
        # B_Dynamics = PARAMETERS_LIST[4].copy()
        # D_Dynamics = PARAMETERS_LIST[5].copy()

        # B_Dynamics = B_Dynamics_Nominal.copy()


        # ETA_CHARGING_VALUES = np.array([[0.9],
        #                                 [0.7],
        #                                 [0.5],
        #                                 [0.3]])
        # ETA_DISCHARGING_VALUES = np.array([[1/0.9],
        #                                     [1/0.7],
        #                                     [1/0.5],
        #                                     [1/0.3]])

        # for i in range(0,NUMBER_ATOMIC_AGENTS):
            
        #     e_i_MAX = UPPER_BOUNDS_STATE[2,i]
        #     e_i_Percentage = (x_evolution[(i*NUM_STATES)+2,k]*100)/e_i_MAX 
        #     Eta = 0 
        #     if u_evolution[(i*2)+1,k] >= 0:
        #         if 0 <= e_i_Percentage < 25:
        #             Eta = ETA_CHARGING_VALUES[0,0]
        #         elif 25 <= e_i_Percentage < 50:
        #             Eta = ETA_CHARGING_VALUES[1,0]
        #         elif 50 <= e_i_Percentage < 75:
        #             Eta = ETA_CHARGING_VALUES[2,0]
        #         elif 75 <= e_i_Percentage <= 100:
        #             Eta = ETA_CHARGING_VALUES[3,0]

        #     elif u_evolution[(i*2)+1,k] < 0:
        #         if 0 <= e_i_Percentage < 25:
        #             Eta = ETA_DISCHARGING_VALUES[0,0]
        #         elif 25 <= e_i_Percentage < 50:
        #             Eta = ETA_DISCHARGING_VALUES[1,0]
        #         elif 50 <= e_i_Percentage < 75:
        #             Eta = ETA_DISCHARGING_VALUES[2,0]
        #         elif 75 <= e_i_Percentage <= 100:
        #             Eta = ETA_DISCHARGING_VALUES[3,0]

        #     B_Dynamics[(i*NUM_STATES)+2,(i*2)+1] = TAU*Eta

        # State update using PWA dynamics and global solution
        print("Mean evolution error norm = ", (np.linalg.norm(Reference_Signal[:,k] - x_evolution[:,k]))/NUMBER_ATOMIC_AGENTS)
        Simulation_Timer_End = tm.time() - Simulation_Timer_Start
        print("Enlapsed time:", round(Simulation_Timer_End,2), "[s]")
        print("Expected time to finish:", round(((Simulation_Timer_End*SIMULATION_HORIZON)/(k+1)) - Simulation_Timer_End, 2), "[s]")

        x_evolution[:,k+1] =  EEA_ENB.step(u_evolution[:,k], w_evolution[:,k])
    
        # x_evolution[:,k+1] =  A_Dynamics @ x_evolution[:,k] + B_Dynamics @ u_evolution[:,k] + D_Dynamics @ w_evolution[:,k]
        w_evolution[:,k+1] = w_measured[:,k+1].copy()
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
    