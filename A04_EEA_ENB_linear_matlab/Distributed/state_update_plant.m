function [x_plus, Pedge, PedgeTotal] = state_update_plant(x_h, u_h, w_h, Parameters)



[Input_Nodes, State_Nodes, A, B, D, Atomic_Agents, Atomic_Agents_Matrices] = system_dynamics(Parameters);

    
x_plus = A*x_h + B*u_h + D*w_h;

Pedge = 0;
PedgeTotal = 0;
    
end