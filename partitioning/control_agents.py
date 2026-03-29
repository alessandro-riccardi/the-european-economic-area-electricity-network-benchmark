import numpy as np


def compute_control_agents_matrices_linear(LIST_ATOMIC_AGENTS, Control_Agents, Augmented_Control_Agents, EEA_ENB, Q, R):
    NUMBER_CONTROL_AGENTS = len(Control_Agents)

    NUM_STATES = EEA_ENB.NUM_STATES
    NUM_INPUTS = EEA_ENB.NUM_INPUTS

    A_Dynamics = EEA_ENB.A_Dynamics.copy()
    B_Dynamics = EEA_ENB.B_Dynamics.copy()
    D_Dynamics = EEA_ENB.D_Dynamics.copy()
    
    Control_Agents_Matrices = [[] for _ in range(NUMBER_CONTROL_AGENTS)]

    for i in range(NUMBER_CONTROL_AGENTS):
        Control_Agents_Matrices[i] = [[] for _ in range(7)]

    for l in range(0,NUMBER_CONTROL_AGENTS):

        Size_Augmented_Control_Agent = len(Augmented_Control_Agents[l])
        
        A_Augmented = np.zeros((NUM_STATES*Size_Augmented_Control_Agent,NUM_STATES*Size_Augmented_Control_Agent))
        B_Augmented = np.zeros((NUM_STATES*Size_Augmented_Control_Agent,NUM_INPUTS*Size_Augmented_Control_Agent))
        # Bu_Augmented = np.zeros((NUM_STATES*Size_Augmented_Control_Agent,Size_Augmented_Control_Agent))
        # Bz_Augmented = np.zeros((NUM_STATES*Size_Augmented_Control_Agent,8*Size_Augmented_Control_Agent))
        D_Augmented = np.zeros((NUM_STATES*Size_Augmented_Control_Agent,2*Size_Augmented_Control_Agent))
        Q_Augmented = np.zeros((NUM_STATES*Size_Augmented_Control_Agent,NUM_STATES*Size_Augmented_Control_Agent))
        R_Augmented = np.zeros((NUM_INPUTS*Size_Augmented_Control_Agent,NUM_INPUTS*Size_Augmented_Control_Agent))

        for i in range(0, Size_Augmented_Control_Agent):
            Agent_Index_1 = LIST_ATOMIC_AGENTS.index(Augmented_Control_Agents[l][i])
            for j in range(0, Size_Augmented_Control_Agent):
                Agent_Index_2 = LIST_ATOMIC_AGENTS.index(Augmented_Control_Agents[l][j])
                A_Augmented[i*NUM_STATES:(i+1)*NUM_STATES,j*NUM_STATES:(j+1)*NUM_STATES] = A_Dynamics[Agent_Index_1*NUM_STATES:(Agent_Index_1+1)*NUM_STATES,Agent_Index_2*NUM_STATES:(Agent_Index_2+1)*NUM_STATES].copy()
                B_Augmented[i*NUM_STATES:(i+1)*NUM_STATES,j*NUM_INPUTS:(j+1)*NUM_INPUTS] = B_Dynamics[Agent_Index_1*NUM_STATES:(Agent_Index_1+1)*NUM_STATES, Agent_Index_2*NUM_INPUTS:(Agent_Index_2+1)*NUM_INPUTS].copy()
                # Bu_Augmented[i*NUM_STATES:(i+1)*NUM_STATES,j] = Bu_MLD[Agent_Index_1*NUM_STATES:(Agent_Index_1+1)*NUM_STATES, Agent_Index_2].copy()
                # Bz_Augmented[i*NUM_STATES:(i+1)*NUM_STATES,j*8:(j+1)*8] = Bz_MLD[Agent_Index_1*NUM_STATES:(Agent_Index_1+1)*NUM_STATES,Agent_Index_2*8:(Agent_Index_2+1)*8].copy()
                D_Augmented[i*NUM_STATES:(i+1)*NUM_STATES,j*2:(j+1)*2] = D_Dynamics[Agent_Index_1*NUM_STATES:(Agent_Index_1+1)*NUM_STATES,Agent_Index_2*2:(Agent_Index_2+1)*2].copy()
                Q_Augmented[i*NUM_STATES:(i+1)*NUM_STATES,j*NUM_STATES:(j+1)*NUM_STATES] = Q[Agent_Index_1*NUM_STATES:(Agent_Index_1+1)*NUM_STATES,Agent_Index_2*NUM_STATES:(Agent_Index_2+1)*NUM_STATES].copy()
                R_Augmented[i*NUM_INPUTS:(i+1)*NUM_INPUTS,j*NUM_INPUTS:(j+1)*NUM_INPUTS] = R[Agent_Index_1*NUM_INPUTS:(Agent_Index_1+1)*NUM_INPUTS,Agent_Index_2*NUM_INPUTS:(Agent_Index_2+1)*NUM_INPUTS].copy()
                # R_Augmented[i,j] = R[Agent_Index_1, Agent_Index_2].copy()
        
        Control_Agents_Matrices[l][0] = A_Augmented.copy()
        Control_Agents_Matrices[l][1] = B_Augmented.copy()
        Control_Agents_Matrices[l][2] = Q_Augmented.copy()
        Control_Agents_Matrices[l][3] = R_Augmented.copy()
        # Control_Agents_Matrices[l][4] = Bz_Augmented.copy()
        Control_Agents_Matrices[l][5] = D_Augmented.copy()
        Control_Agents_Matrices[l][6] = B_Augmented.copy()

    return Control_Agents_Matrices

def compute_control_agents_matrices(model, LIST_ATOMIC_AGENTS, Control_Agents, Augmented_Control_Agents, EEA_ENB, Q, R):
    if model == 'linear':
        return compute_control_agents_matrices_linear(LIST_ATOMIC_AGENTS, Control_Agents, Augmented_Control_Agents, EEA_ENB, Q, R)
    else:
        # Here add the hybrid model augmented control agents matrices computation when the function is implemented
        raise ValueError(f"Model '{model}' not recognized. Please choose 'linear'.")