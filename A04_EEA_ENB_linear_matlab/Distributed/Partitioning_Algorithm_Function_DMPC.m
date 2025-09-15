function [Control_Agents, Control_Agents_Matrices, Control_Agents_Indexes, Delta] = Partitioning_Algorithm_Function_DMPC(Input_Nodes, State_Nodes, A, B, Atomic_Agents, Atomic_Agents_Matrices, Parameters, experiment_id, Store_Results)

%% Preliminary Operations

Na = Parameters{7};

number_of_inputs = size(Input_Nodes,2);
number_of_states = size(State_Nodes,2);
number_of_atomic_agents = Na; 


%% Partitioning State Transition Matrix in Atomic Agents

Size_Atomic_Agents = zeros(number_of_atomic_agents,1);


for k = 1:number_of_atomic_agents
    n_states = 0;
    for i = 1:size(Atomic_Agents{k},2)
        if is_in(Atomic_Agents{k}(i),State_Nodes)
            n_states = n_states + 1;
        end
    end
    Size_Atomic_Agents(k) = n_states;
end

A_Agents_Matrices = cell(number_of_atomic_agents,number_of_atomic_agents);

global_i = 1;
for i = 1:number_of_atomic_agents
    global_j = 1;
    for j = 1:number_of_atomic_agents
        A_Agents_Matrices{i,j} = A(global_i:global_i+Size_Atomic_Agents(i)-1,global_j:global_j+Size_Atomic_Agents(j)-1);
        global_j = global_j+Size_Atomic_Agents(j);
        % pause();
    end
    global_i = global_i+Size_Atomic_Agents(i);
end

%% Optimization-Based Partitioning

numVar = number_of_atomic_agents*number_of_atomic_agents;


lbI = 0*ones(1,numVar);
ubI = 1*ones(1,numVar);

Aeq = zeros(number_of_atomic_agents,number_of_atomic_agents);

global_idx = 1;
for i = 1:number_of_atomic_agents
    Aeq(i,global_idx:global_idx+number_of_atomic_agents-1) = ones(1,number_of_atomic_agents);
    global_idx = global_idx+number_of_atomic_agents;
end

beq = ones(number_of_atomic_agents,1);

settingsGA = optimoptions('ga' , 'Display' , 'iter', 'PlotFcn', @gaplotbestf);

[solI,~,~,~] = ga(@(delta)Partitioning_Index_DMPC(delta,A,Atomic_Agents,State_Nodes),numVar,[],[],Aeq,beq,lbI,ubI,[],1:numVar,settingsGA);


%% Solution Recontruction

Delta = zeros(number_of_atomic_agents);
k = 1;

for i = 1:number_of_atomic_agents
    for j = 1:number_of_atomic_agents
        Delta(i,j) = solI(k);
        k = k + 1;
    end
end

%% Control Agents

Control_Agents = cell(number_of_atomic_agents,1);
Control_Agents_Indexes = cell(number_of_atomic_agents,1);

for i = 1:number_of_atomic_agents
    for j = 1:number_of_atomic_agents
        if Delta(i,j) == 1
            Control_Agents{j} = [Control_Agents{j}, Atomic_Agents{i}];
            Control_Agents_Indexes{j} = [Control_Agents_Indexes{j}, i];
        end
    end
end

%% Remove empty agents

number_of_control_agents = 0;

% Compute the number of atomic agents
for k = 1:number_of_atomic_agents
    if isempty(Control_Agents{k}) == false        
        number_of_control_agents = number_of_control_agents + 1;
    end
end

% Reorganize the list of atomic agents
temp_cell = cell(number_of_control_agents,1);
temp_cell_indexes = cell(number_of_control_agents,1);
temp_idx = 1;

for k = 1:number_of_atomic_agents
    if isempty(Control_Agents{k}) == false        
        temp_cell{temp_idx} = Control_Agents{k};
        temp_cell_indexes{temp_idx} = Control_Agents_Indexes{k};
        temp_idx = temp_idx + 1;
    end
end

% clear Atomic_Agents
Control_Agents = temp_cell;
Control_Agents_Indexes = temp_cell_indexes;


%% Control Agents Matrices
Control_Agents_Matrices = cell(number_of_control_agents,1);

for k = 1:number_of_control_agents

    number_of_agents = size(Control_Agents_Indexes{k},2);

    A_Si = zeros(3*number_of_agents);
    A_Si_inter = zeros(number_of_states);
    B_Si = zeros(3*number_of_agents);

    sub_index = 1;

    for i = 1:number_of_agents
        agent_index =  Control_Agents_Indexes{k}(i);
        A_Si(sub_index:sub_index+2,sub_index:sub_index+2) = A((agent_index-1)*3+1:(agent_index-1)*3+3,(agent_index-1)*3+1:(agent_index-1)*3+3);
        B_Si(sub_index:sub_index+2,sub_index:sub_index+2) = B((agent_index-1)*3+1:(agent_index-1)*3+3,(agent_index-1)*3+1:(agent_index-1)*3+3);
        sub_index_interaction = 1;
        for j = 1:number_of_agents
            agent_interaction_index =  Control_Agents_Indexes{k}(j);
            if i ~= j                
                A_Si(sub_index:sub_index+2,sub_index_interaction:sub_index_interaction+2) = A((agent_index-1)*3+1:(agent_index-1)*3+3,(agent_interaction_index-1)*3+1:(agent_interaction_index-1)*3+3);
            end
            
            sub_index_interaction = sub_index_interaction + 3;
        end
        sub_index = sub_index + 3;
        A_Si_inter((agent_index-1)*3+1:(agent_index-1)*3+3,:) = A((agent_index-1)*3+1:(agent_index-1)*3+3,:);
        A_Si_inter((agent_index-1)*3+1:(agent_index-1)*3+3,(agent_index-1)*3+1:(agent_index-1)*3+3) = zeros(3);
    end
    

    Control_Agents_Matrices{k} = {A_Si, A_Si_inter, B_Si};

end



%% Intra-agent Interaction

W_intra = zeros(number_of_control_agents,1);
W_intra_total = 0;
for k = 1:number_of_control_agents
    if isempty(Control_Agents_Matrices{k}{1}) == false
        W_intra_total = W_intra_total + norm(Control_Agents_Matrices{k}{1},"fro");
    end
end

for k = 1:number_of_control_agents
    if isempty(Control_Agents_Matrices{k}{1}) == false
        W_intra(k,1) = (norm(Control_Agents_Matrices{k}{1},"fro"))/(1+W_intra_total);
    end
end

%% Inter-agent Interaction

W_inter = zeros(number_of_control_agents,1);
W_inter_total = 0;

for k = 1:number_of_control_agents
    if isempty(Control_Agents_Matrices{k}{2}) == false
        W_inter_total = W_inter_total + norm(Control_Agents_Matrices{k}{2},"fro");
    end
end

for k = 1:number_of_control_agents
    if isempty(Control_Agents_Matrices{k}{2}) == false
        W_inter(k,1) = (norm(Control_Agents_Matrices{k}{2},"fro"))/(1+W_inter_total);
    end
end

%% Output

number_of_inputs
number_of_atomic_agents
number_of_control_agents
Atomic_Agents
Control_Agents

%% Store results

if Store_Results == true
file_name_system = ['SimulationOutput/',experiment_id, '_System.csv'];
file_name_atomic = ['SimulationOutput/',experiment_id, '_AtomicAgents.csv'];
file_name_atomic_matrices = ['SimulationOutput/',experiment_id, '_AtomicAgentsMatrices.csv'];
file_name_atomic_interactions = ['SimulationOutput/',experiment_id, '_AtomicAgentsInteractions.csv'];
file_name_control = ['SimulationOutput/',experiment_id, '_ControlAgents.csv'];
file_name_control_matrices = ['SimulationOutput/',experiment_id, '_ControlAgentsMatrices.csv'];
file_name_control_interactions = ['SimulationOutput/',experiment_id, '_ControlAgentsInteractions.csv'];
end
%% Write Atomic Agents Matrices
if Store_Results == true
    empty_raw = NaN(1,number_of_states);
    
    writematrix(empty_raw, file_name_atomic_matrices)
    
    for k = 1:number_of_atomic_agents
        writematrix(Atomic_Agents_Matrices{k}{1}, file_name_atomic_matrices,'WriteMode','append')
    end
    
    writematrix(empty_raw, file_name_atomic_interactions)
    
    raw_idx = 1;
    for k = 1:number_of_atomic_agents
        writematrix(Atomic_Agents_Matrices{k}{2}(raw_idx:raw_idx+Size_Atomic_Agents(k)-1,:), file_name_atomic_interactions,'WriteMode','append')
        raw_idx = raw_idx+Size_Atomic_Agents(k);
    end
end
%% Write Control Agents Matrices

if Store_Results == true

empty_raw = NaN(1,number_of_states);

writematrix(empty_raw, file_name_control_matrices)

for k = 1:number_of_control_agents
    writematrix(Control_Agents_Matrices{k}{1}, file_name_control_matrices,'WriteMode','append')
end

Size_Control_Agents = zeros(number_of_control_agents,1);


for k = 1:number_of_control_agents
    n_states = 0;
    for i = 1:size(Control_Agents{k},2)
        if is_in(Control_Agents{k}(i),State_Nodes)
            n_states = n_states + 1;
        end
    end
    Size_Control_Agents(k) = n_states;
end


writematrix(empty_raw, file_name_control_interactions)

raw_idx = 1;
for k = 1:number_of_control_agents
    writematrix(Control_Agents_Matrices{k}{2}(raw_idx:raw_idx+Size_Control_Agents(k)-1,:), file_name_control_interactions,'WriteMode','append')
    raw_idx = raw_idx+Size_Control_Agents(k);
end

end

%% Write System

if Store_Results == true

    writematrix(empty_raw, file_name_system)
    
    writematrix([number_of_inputs, number_of_states], file_name_system,'WriteMode','append')
    
    writematrix(empty_raw, file_name_system,'WriteMode','append')
    
    writematrix(Input_Nodes, file_name_system,'WriteMode','append')
    
    writematrix(empty_raw, file_name_system,'WriteMode','append')
    
    writematrix(State_Nodes, file_name_system,'WriteMode','append')
    
    writematrix(empty_raw, file_name_system,'WriteMode','append')
    
    writematrix(B, file_name_system,'WriteMode','append')
    
    writematrix(empty_raw, file_name_system,'WriteMode','append')
    
    writematrix(A, file_name_system,'WriteMode','append')

end

%%  Atomic Agents and Atomic Agents Matrics
if Store_Results == true
    writematrix(empty_raw, file_name_atomic)
    writematrix(number_of_atomic_agents, file_name_atomic,'WriteMode','append')
    writematrix(empty_raw, file_name_atomic,'WriteMode','append')

    for k = 1:number_of_atomic_agents
        writematrix(Atomic_Agents{k}, file_name_atomic,'WriteMode','append')
    end
    
    writematrix(empty_raw, file_name_atomic,'WriteMode','append')
    for k = 1:number_of_atomic_agents
        writematrix(Atomic_Agents_Matrices{k}{1}, file_name_atomic,'WriteMode','append')
        writematrix(empty_raw, file_name_atomic,'WriteMode','append')
        writematrix(Atomic_Agents_Matrices{k}{2}, file_name_atomic,'WriteMode','append')
        writematrix(empty_raw, file_name_atomic,'WriteMode','append')
    end

end
%% Control Agents and Control Agents Matrices

if Store_Results == true
        writematrix(empty_raw, file_name_control)
        writematrix(number_of_control_agents, file_name_control,'WriteMode','append')
        writematrix(empty_raw, file_name_control,'WriteMode','append')
    for k = 1:number_of_control_agents
        writematrix(Control_Agents{k}, file_name_control,'WriteMode','append')
    end
    writematrix(empty_raw, file_name_control,'WriteMode','append')
    for k = 1:number_of_control_agents
        writematrix(Control_Agents_Matrices{k}{1}, file_name_control,'WriteMode','append')
        writematrix(empty_raw, file_name_control,'WriteMode','append')
        writematrix(Control_Agents_Matrices{k}{2}, file_name_control,'WriteMode','append')
        writematrix(empty_raw, file_name_control,'WriteMode','append')
    end
end

end


%% Auxiliary Functions

function is_member = check_list_member(item, list)
    is_member = false;
    for k = 1:size(list,1)
        if ismember(item, list{k}) == true
            is_member = true;
        end
    end
end

function index = find_list_index(item, list)
    index = 0;
    for k = 1:size(list,1)
        if ismember(item, list{k}) == true
            index = k;
        end
    end
end

function A_out = swap_columns(A_in, i, j)
    col_i = A_in(:,i);
    A_in(:,i) = A_in(:,j);
    A_in(:,j) = col_i;
    A_out = A_in;
end

function A_out = swap_raws(A_in, i, j)
    raw_i = A_in(i,:);
    A_in(i,:) = A_in(j,:);
    A_in(j,:) = raw_i;
    A_out = A_in;
end

function is_in = is_in(item, array)
    is_in = false;

    if max(array == item) == true
        is_in = true;
    end

end




