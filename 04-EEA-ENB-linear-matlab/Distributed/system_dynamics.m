function [Input_Nodes, State_Nodes, A, B, D, Atomic_Agents, Atomic_Agents_Matrices] = system_dynamics(Parameters)


%% Definition of the state dynamics

DT = Parameters{2};
Na = Parameters{7};

Adj = Parameters{21};
Adj_W = Parameters{22};

KLine = Parameters{27};

Kp = Parameters{10};
Tp = Parameters{11};
nc = Parameters{12};
nd = Parameters{13};
number_of_inputs = 3*Na;
number_of_states = 3*Na;

Input_Nodes = 1:number_of_inputs;
State_Nodes = number_of_inputs+1:number_of_inputs+number_of_states;

Atomic_Agents = cell(Na,1);

A = zeros(3*Na);
B = zeros(3*Na);
D = zeros(3*Na,2*Na);

global_input_idx = 1;
global_state_idx = number_of_inputs+1;

for i = 1:Na
    
    Kii = 0;

    for k = 1:Na
        if Adj(i,k) == 1 
            Kii = Kii + ((DT*Kp(i))/Tp(i))*(KLine/Adj_W(i,k));
        end
    end

    Ai = [1   DT*2*pi          0;
          Kii (1 - (DT/Tp(i))) 0;
          0   0                1];

    Bi = [0 0 0 ; (DT*Kp(i))/Tp(i) -(DT*Kp(i))/Tp(i) (DT*Kp(i))/Tp(i); 0 DT*nc(i) -DT*nd(i)];

    Di = [0 0;
          -(DT*Kp(i))/Tp(i) (DT*Kp(i))/Tp(i);
          0 0];    
        
    A((i-1)*3+1:i*3,(i-1)*3+1:i*3) = Ai;
    B((i-1)*3+1:i*3,(i-1)*3+1:i*3) = Bi;
    D((i-1)*3+1:i*3,(i-1)*2+1:i*2) = Di;
    
    for k = 1:Na
        if Adj(i,k) == 1 
            A((i-1)*3+2,(k-1)*3+1) = -((DT*Kp(i))/Tp(i))*(KLine/Adj_W(i,k));
        end
    end

    Atomic_Agents{i} = [global_input_idx:global_input_idx+2,global_state_idx:global_state_idx+2];
    global_input_idx = global_input_idx + 3;
    global_state_idx = global_state_idx + 3;

end

number_of_atomic_agents = Na;

Atomic_Agents_Matrices = cell(number_of_atomic_agents,1);

global_idx = 1;

for k = 1:number_of_atomic_agents

    n_states = 0;

    for i = 1:size(Atomic_Agents{k},2)
        if is_in(Atomic_Agents{k}(i),State_Nodes)
            n_states = n_states + 1;
        end
    end

    A_agent = A(global_idx:global_idx+n_states-1,global_idx:global_idx+n_states-1);
    A_inter = zeros(number_of_states,number_of_states);
    A_inter(global_idx:global_idx+n_states-1,:) = A(global_idx:global_idx+n_states-1,:);
    A_inter(:,global_idx:global_idx+n_states-1) = A(:,global_idx:global_idx+n_states-1);
    A_inter(global_idx:global_idx+n_states-1,global_idx:global_idx+n_states-1) = zeros(n_states);


    Atomic_Agents_Matrices{k} = {A_agent, A_inter};
    global_idx = global_idx + n_states;

end


end


%% Auxiliary Functions


function is_in = is_in(item, array)
    is_in = false;

    if max(array == item) == true
        is_in = true;
    end

end