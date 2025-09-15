function p_idx = Partitioning_Index_DMPC(delta,A,Atomic_Agents,State_Nodes)

number_of_atomic_agents = size(Atomic_Agents,1);
number_of_states = size(State_Nodes,2);
%% Indexing optimization variable
Delta = zeros(number_of_atomic_agents);
k = 1;

for i = 1:number_of_atomic_agents
    for j = 1:number_of_atomic_agents
        Delta(i,j) = delta(k);
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
        temp_cell{temp_idx,1} = Control_Agents{k};
        temp_cell_indexes{temp_idx} = Control_Agents_Indexes{k};
        temp_idx = temp_idx + 1;
    end
end

clear Control_Agents
Control_Agents = temp_cell;
Control_Agents_Indexes = temp_cell_indexes;


%% Sort Control Agents


for k = 1:number_of_control_agents
    Control_Agents{k} = sort(Control_Agents{k});
end
% Control_Agents

%% Reshaping System
global_idx = 1;

for k = 1:number_of_control_agents
    for i = 1:size(Control_Agents{k},2)
        if is_in(Control_Agents{k}(i),State_Nodes)
            i_idx = find(State_Nodes == Control_Agents{k}(i));
            A = swap_columns(A, i_idx, global_idx);
            A = swap_raws(A, i_idx, global_idx);
            % B = swap_raws(B, i_idx, global_idx);
            State_Nodes = swap_columns(State_Nodes, i_idx, global_idx);
            global_idx = global_idx + 1;
        end
    end
end

%% Atomic Agents Matrices

Control_Agents_Matrices = cell(number_of_control_agents,1);

global_idx = 1;

for k = 1:number_of_control_agents

    n_states = 0;

    for i = 1:size(Control_Agents{k},2)
        if is_in(Control_Agents{k}(i),State_Nodes)
            n_states = n_states + 1;
        end
    end

    A_agent = A(global_idx:global_idx+n_states-1,global_idx:global_idx+n_states-1);
    A_inter = zeros(number_of_states,number_of_states);
    A_inter(global_idx:global_idx+n_states-1,:) = A(global_idx:global_idx+n_states-1,:);
    A_inter(:,global_idx:global_idx+n_states-1) = A(:,global_idx:global_idx+n_states-1);
    A_inter(global_idx:global_idx+n_states-1,global_idx:global_idx+n_states-1) = zeros(n_states);

    Control_Agents_Matrices{k} = {A_agent, A_inter};
    global_idx = global_idx + n_states;

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


%% Definition of DMPC control agents

number_of_control_agents = size(Control_Agents,1);

Control_Agents_DMPC = cell(number_of_control_agents,1);

for i = 1:number_of_control_agents
    Control_Agents_DMPC{i} = Control_Agents{i};
    for j = 1:number_of_control_agents
        if i ~= j
            condition = is_neighbor(Control_Agents_Indexes{i}, Control_Agents_Indexes{j}, A);
            if condition == true
                Control_Agents_DMPC{i} = [Control_Agents_DMPC{i}, Control_Agents{j}];
            end
        end
    end
end


%% Cost Index

% Select one between P_1 and P_2

% Cost index P_1
% Cost_index = 0;
% for l = 1:number_of_control_agents
%     Cost_index = Cost_index + (W_inter(l,1)/(1+W_intra(l,1)))^2 ;
% end

% Cost index P_2
Cost_index = 0;
for l = 1:number_of_control_agents
    Cost_index = Cost_index + (W_inter(l,1)/(1+W_intra(l,1)))^2 + (1/(1+size(Control_Agents_DMPC{l},2)));
end

p_idx = Cost_index;


end

%% Support Functions

function is_in = is_in(item, array)
    is_in = false;

    if max(array == item) == true
        is_in = true;
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

function condition = is_neighbor(control_agent_i, control_agent_j, A)
    
    condition = false;
    
    for i = 1:size(control_agent_i,1)
        raw_idx = control_agent_i(i)*3-1;
        for j = 1:size(control_agent_j,1)
            col_idx = (control_agent_j(j)-1)*3 + 1;
            if A(raw_idx,col_idx) ~= 0
                condition = true;
                return
            end
        end
    end

end