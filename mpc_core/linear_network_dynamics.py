import numpy as np
import math as mt

class LinearNetworkDynamics:

    def __init__(self, atomic_agents, Weighted_Adjacency_Matrix, control_time_step, intertia_modifiers, compute_initial_state_linear, INITIAL_DISPATCHABLE_POWER):

        self.x = compute_initial_state_linear(atomic_agents, INITIAL_DISPATCHABLE_POWER)

        self.NUMBER_ATOMIC_AGENTS = len(atomic_agents)
        self.NUM_STATES = 5
        self.NUM_INPUTS = 3
        self.TAU = control_time_step

        # Build system dynamics
        self.A_Dynamics = np.zeros((self.NUM_STATES*self.NUMBER_ATOMIC_AGENTS,self.NUM_STATES*self.NUMBER_ATOMIC_AGENTS))
        self.B_Dynamics = np.zeros((self.NUM_STATES*self.NUMBER_ATOMIC_AGENTS,self.NUM_INPUTS*self.NUMBER_ATOMIC_AGENTS))
        # B_Dynamics_Nominal = np.zeros((NUM_STATES*NUMBER_ATOMIC_AGENTS,NUM_INPUTS*NUMBER_ATOMIC_AGENTS))
        self.D_Dynamics = np.zeros((self.NUM_STATES*self.NUMBER_ATOMIC_AGENTS,2*self.NUMBER_ATOMIC_AGENTS))

        self.Line_Impedance = 1 
        self.Kp_i = 0.05
        self.Tr_nominal = 25

        for i in range(0,self.NUMBER_ATOMIC_AGENTS):
            
            # Inertia modifiers
            Tr_i = self.Tr_nominal * intertia_modifiers[i]

            Kii = 0
            Lii = 0 
            for j in range(0,self.NUMBER_ATOMIC_AGENTS):
                if Weighted_Adjacency_Matrix[i,j] != 0:
                    Kii = Kii + (((self.TAU*self.Kp_i)/(Tr_i))*(self.Line_Impedance/Weighted_Adjacency_Matrix[i,j]))
                    Lii = Lii + self.TAU * (self.Line_Impedance / Weighted_Adjacency_Matrix[i, j])

            A_i = [[1,    self.TAU*2*mt.pi,      0, 0, 0],
                [-Kii, (1 - (self.TAU/Tr_i)), 0, 0, 0],
                [0,    0,                1, 0, 0],
                [Lii, 0,                0, 1, 0], 
                [0,    0,                0, 0, 1]]

                
            # B_i_nominal = [[0,               0],
            #                [(Kp_i*TAU)/Tr_i, -(Kp_i*TAU)/Tr_i],
            #                [0,               1], # HERE THE VALUE MUST BE TAUS*ETA_i^j, BUT WE ASSING IT AFTERWARDS
            #                [0,               0],
            #                [TAU,               0]]
            
            ETA_c = 0.9
            ETA_d = 1/0.9

            B_i = [[0,               0,                0],
                [(self.Kp_i*self.TAU)/Tr_i, -(self.Kp_i*self.TAU)/Tr_i, (self.Kp_i*self.TAU)/Tr_i],
                [0,               self.TAU*ETA_c,        -self.TAU*ETA_d], 
                [0,               0,                0],
                [self.TAU,             0,                0]]
            
            D_i = [[0,                0],
                [-(self.Kp_i*self.TAU)/Tr_i, (self.Kp_i*self.TAU)/Tr_i],
                [0,                0],
                [0,                0],
                [0,                0]]
            
            self.A_Dynamics[i*self.NUM_STATES:(i+1)*self.NUM_STATES,i*self.NUM_STATES:(i+1)*self.NUM_STATES] = A_i.copy()
            self.B_Dynamics[i*self.NUM_STATES:(i+1)*self.NUM_STATES,i*self.NUM_INPUTS:(i+1)*self.NUM_INPUTS] = B_i.copy()
            # B_Dynamics_Nominal[i*NUM_STATES:(i+1)*NUM_STATES,i*NUM_INPUTS:(i+1)*NUM_INPUTS] = B_i_nominal.copy()
            self.D_Dynamics[i*self.NUM_STATES:(i+1)*self.NUM_STATES,i*2:(i+1)*2] = D_i.copy()

            for j in range(0,self.NUMBER_ATOMIC_AGENTS):
                if Weighted_Adjacency_Matrix[i,j] != 0:
                    self.A_Dynamics[(i*self.NUM_STATES)+1,j*self.NUM_STATES] = ((self.TAU*self.Kp_i)/(Tr_i))*(self.Line_Impedance/Weighted_Adjacency_Matrix[i,j])
                    self.A_Dynamics[(i*self.NUM_STATES)+3,j*self.NUM_STATES] = -self.TAU*(self.Line_Impedance/Weighted_Adjacency_Matrix[i,j])


    def step(self, u):
        x_plus = self.A_Dynamics @ self.x + self.B_Dynamics @ u
        self.x = x_plus
        return self.x
    

