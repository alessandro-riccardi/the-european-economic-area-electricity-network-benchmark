import numpy as np


def compute_optimization_matrices_linear(model, Control_Agents, Augmented_Control_Agents, Control_Agents_Matrices, PREDICTION_HORIZON, EEA_ENB):
    
    NUMBER_CONTROL_AGENTS = len(Control_Agents)
    NUM_STATES = EEA_ENB.NUM_STATES
    NUM_INPUTS = EEA_ENB.NUM_INPUTS

    Control_Agents_Optimization_Matrices = [[] for _ in range(NUMBER_CONTROL_AGENTS)]

    for i in range(NUMBER_CONTROL_AGENTS):
        Control_Agents_Optimization_Matrices[i] = [[] for _ in range(8)]

    for l in range(0,NUMBER_CONTROL_AGENTS):
        Size_Augmented_Control_Agent = len(Augmented_Control_Agents[l])

        M_Optimization = np.zeros((NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON,NUM_STATES*Size_Augmented_Control_Agent), dtype=np.float64)
        C_Optimization = np.zeros((NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON,NUM_INPUTS*Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)
        # Cu_Optimization = np.zeros((NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON,Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)
        # Cz_Optimization = np.zeros((NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON,8*Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)
        D_Optimization = np.zeros((NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON,2*Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)

        A_Augmented = Control_Agents_Matrices[l][0].copy()
        B_Augmented = Control_Agents_Matrices[l][1].copy()
        # Bu_Augmented = Control_Agents_Matrices[l][1].copy()
        # Bz_Augmented = Control_Agents_Matrices[l][4].copy()
        D_Augmented = Control_Agents_Matrices[l][5].copy()

        Row_Index = 0
        for i in range(1,PREDICTION_HORIZON+1):

            M_Optimization[Row_Index:Row_Index+NUM_STATES*Size_Augmented_Control_Agent,:] = np.linalg.matrix_power(A_Augmented,i)
            
            Col_Index_1 = 0
            Col_Index_2 = 0
            Col_Index_3 = 0
            Col_Index_4 = 0
            for j in reversed(range(0,i)):
                C_Optimization[Row_Index:Row_Index+NUM_STATES*Size_Augmented_Control_Agent,Col_Index_1:Col_Index_1+NUM_INPUTS*Size_Augmented_Control_Agent] = np.linalg.matrix_power(A_Augmented,j) @ B_Augmented
                # C_Optimization[Row_Index:Row_Index+NUM_STATES*Size_Augmented_Control_Agent,Col_Index_2:Col_Index_2+Size_Augmented_Control_Agent] = np.linalg.matrix_power(A_Augmented,j) @ B_Augmented
                # Cz_Optimization[Row_Index:Row_Index+NUM_STATES*Size_Augmented_Control_Agent,Col_Index_3:Col_Index_3+8*Size_Augmented_Control_Agent] = np.linalg.matrix_power(A_Augmented,j) @ Bz_Augmented
                D_Optimization[Row_Index:Row_Index+NUM_STATES*Size_Augmented_Control_Agent,Col_Index_4:Col_Index_4+2*Size_Augmented_Control_Agent] = np.linalg.matrix_power(A_Augmented,j) @ D_Augmented
                Col_Index_4 += 2*Size_Augmented_Control_Agent
                Col_Index_1 += NUM_INPUTS*Size_Augmented_Control_Agent
                Col_Index_2 += Size_Augmented_Control_Agent
                Col_Index_3 += 8*Size_Augmented_Control_Agent
                # print(j)

            Row_Index = Row_Index + NUM_STATES*Size_Augmented_Control_Agent
        
        Control_Agents_Optimization_Matrices[l][0] = M_Optimization.copy()
        Control_Agents_Optimization_Matrices[l][1] = C_Optimization.copy()
        # Control_Agents_Optimization_Matrices[l][4] = Cz_Optimization.copy()
        Control_Agents_Optimization_Matrices[l][5] = D_Optimization.copy()
        # Control_Agents_Optimization_Matrices[l][6] = C_Optimization.copy()
        
        Q_Augmented = Control_Agents_Matrices[l][2].copy()
        R_Augmented = Control_Agents_Matrices[l][3].copy()

        Q_Optimization = np.zeros((NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON,NUM_STATES*Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)
        R_Optimization = np.zeros((NUM_INPUTS*Size_Augmented_Control_Agent*PREDICTION_HORIZON,NUM_INPUTS*Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)
        # R_Optimization_PWA = np.zeros((NUM_INPUTS*Size_Augmented_Control_Agent*PREDICTION_HORIZON,NUM_INPUTS*Size_Augmented_Control_Agent*PREDICTION_HORIZON), dtype=np.float64)

        Pos_Index = 0
        for i in range(0,PREDICTION_HORIZON):
            Q_Optimization[Pos_Index:Pos_Index+NUM_STATES*Size_Augmented_Control_Agent,Pos_Index:Pos_Index+NUM_STATES*Size_Augmented_Control_Agent] = Q_Augmented.copy()
            Pos_Index = Pos_Index + NUM_STATES*Size_Augmented_Control_Agent

        Pos_Index = 0
        for i in range(0,PREDICTION_HORIZON):
            R_Optimization[Pos_Index:Pos_Index+NUM_INPUTS*Size_Augmented_Control_Agent,Pos_Index:Pos_Index+NUM_INPUTS*Size_Augmented_Control_Agent] = R_Augmented.copy()
            Pos_Index = Pos_Index + NUM_INPUTS*Size_Augmented_Control_Agent

        # R_Optimization = np.zeros((NUM_INPUTS*PREDICTION_HORIZON*Size_Augmented_Control_Agent,NUM_INPUTS*PREDICTION_HORIZON*Size_Augmented_Control_Agent))
        # for i in range(0,len(R_Optimization)):
        #     R_Optimization[i,i] = 1
        
        # for i in range(0,len(R_Optimization_PWA)):
        #     R_Optimization_PWA[i,i] = 1

        Control_Agents_Optimization_Matrices[l][2] = Q_Optimization.copy()
        Control_Agents_Optimization_Matrices[l][3] = R_Optimization.copy()
        # Control_Agents_Optimization_Matrices[l][7] = R_Optimization_PWA.copy()

    return Control_Agents_Optimization_Matrices

def compute_optimization_matrices(model, Control_Agents, Augmented_Control_Agents, Control_Agents_Matrices, PREDICTION_HORIZON, EEA_ENB):
    if model == 'linear':
        return compute_optimization_matrices_linear(model, Control_Agents, Augmented_Control_Agents, Control_Agents_Matrices, PREDICTION_HORIZON, EEA_ENB)
    else:
        # Here add the hybrid model optimization matrices computation when the function is implemented
        raise ValueError(f"Model '{model}' not recognized. Please choose 'linear'.")