clear all
clc
close all

%% Preliminary Operations

% For reproducibility
rng('default') 

% For notation
format shortE 

% Simulation Name
simID = 'SIM_00_TEST';

% Partitioning selection
% 0: Optimization-Based
% 1: Atomic control agents
% 2: Geographical
% 3: Random
partitioning_selection_index = 1;


%% Simulation Options

% Input Data Plot and Export
plot_input_data = false;
export_input_plot = false;

% Partitioning
load_partitioning = false;
export_partitioning = true;

% Output Data Plot and Export
plot_output_data = true;
export_output_plot = false;
Store_Results = false;

% Display Options
display_iterations = true;
display_percentual = true;

%% Simulation Parameters and Data Import

% Data Import
[Parameters, w_mesured_inter, w_forecast_inter, Pdisp_zero, Delta_w_measured_inter, Delta_w_forecast_inter] = data_import(simID, plot_input_data, export_input_plot);

% Parameters
CountryCodes = Parameters{1};
Na = Parameters{7};
Np = Parameters{8};
N = Parameters{9};
CentoidPositions = Parameters{20};
A = Parameters{21};
AW = Parameters{22};
lb = Parameters{23}';
ub = Parameters{24}';

CISO_Import = Parameters{25};
CapacitiesData = Parameters{26};

ControlSequenceDivision = Parameters{29};
Nu = size(ControlSequenceDivision,1);


[Input_Nodes, State_Nodes, A, B, D, Atomic_Agents, Atomic_Agents_Matrices] = system_dynamics(Parameters);

% Start MPC Timer
tStart = tic;

%% Optimization-Based Partitioning

if partitioning_selection_index == 0
    if load_partitioning == false
        tStartPartitioning = tic;
        [control_agents, control_agents_matrices, control_agents_indexes, delta] = Partitioning_Algorithm_Function_DMPC(Input_Nodes, State_Nodes, A, B, Atomic_Agents, Atomic_Agents_Matrices, Parameters, simID, Store_Results);
        tEndPartitioning = toc(tStartPartitioning);
        disp(['Computation complete. Execution time = ', num2str(tEndPartitioning), ' [s]'])
    
        if export_output_plot == true
            f = gcf();
            exportgraphics(f,['SimulationOutput/',simID,'_Genetic_Algorithm.pdf'],'Resolution',300)
        end
    
        if export_partitioning == true
            save(['SimulationOutput/',simID,'_partitioning.mat'], 'control_agents', 'control_agents_matrices', 'control_agents_indexes', 'delta');
        end
    else
        load(['SimulationOutput/',simID,'_partitioning.mat']);
    end
    number_of_control_agents = size(control_agents,1);
end

%% Comparison with all control agents without partitioning

if partitioning_selection_index == 1

    control_agents = Atomic_Agents;
    control_agents_matrices = Atomic_Agents_Matrices;
    control_agents_indexes = cell(Na,1);
    
    for l = 1:Na
        control_agents_indexes{l} = l;
    end

    number_of_control_agents = size(control_agents,1);

end


%% Geographical Partitioning (Heuristic)

if partitioning_selection_index == 2
    control_agents = Atomic_Agents;
        
    control_agents_indexes{1} = [18, 25, 8];
    control_agents_indexes{2} = [7, 15, 16];
    control_agents_indexes{3} = [21, 3, 11];
    control_agents_indexes{4} = [19, 22, 5];
    control_agents_indexes{5} = [12, 23, 4];
    control_agents_indexes{6} = [14, 1, 26, 10];
    control_agents_indexes{7} = [20, 24, 9];
    control_agents_indexes{8} = [13, 2, 17, 6];
    number_of_control_agents = size(control_agents_indexes,2);
    [control_agents_matrices, control_agents_indexes] = Partitioning_Function_Heuristic(Input_Nodes, State_Nodes, A, B, Atomic_Agents, Atomic_Agents_Matrices, Parameters, simID, Store_Results, control_agents_indexes);
end

%% Random Partitioning

if partitioning_selection_index == 3
    control_agents = Atomic_Agents;
    number_of_control_agents = 8;
    control_agents_indexes = cell(number_of_control_agents,1);
    
    unassigned_atomic_agents = 1:Na;
    
    while ~isempty(unassigned_atomic_agents)
        for l = 1:number_of_control_agents
            if size(unassigned_atomic_agents,2) > 0
                agent_index = randi([1 size(unassigned_atomic_agents,2)]);
    
                control_agents_indexes{l} = [control_agents_indexes{l}, unassigned_atomic_agents(agent_index)];
                unassigned_atomic_agents(agent_index) = [];
            end
        end
    end
    [control_agents_matrices, control_agents_indexes] = Partitioning_Function_Heuristic(Input_Nodes, State_Nodes, A, B, Atomic_Agents, Atomic_Agents_Matrices, Parameters, simID, Store_Results, control_agents_indexes);
end

% Random partitioning used for comparison
% {[22 26 10 7]}
% {[24 23 19 6]}
% {[    4 5 16]}
% {[  25 21 18]}
% {[   15 20 9]}
% {[    3 11 1]}
% {[   8 17 13]}
% {[   14 2 12]}


%% Definition of DMPC ADMM control agents through topology

number_of_atomic_agents = Na;

control_agents_DMPC = cell(number_of_control_agents,1);
control_agents_indexes_DMPC = cell(number_of_control_agents,1);

for i = 1:number_of_control_agents
    control_agents_DMPC{i} = control_agents{i};
    control_agents_indexes_DMPC{i} = control_agents_indexes{i};
    for j = 1:number_of_atomic_agents
        if isempty(control_agents_indexes{i}(control_agents_indexes{i}==j))         % Check is j is an atomic agent of control agent i, if not proceeds
            condition = is_neighbor(control_agents_indexes{i}, j, A);               % Correct this part for adjacency with atoimic agents and not with control agents           
            if condition == true
                control_agents_DMPC{i} = [control_agents_DMPC{i}, Atomic_Agents{j}];
                control_agents_indexes_DMPC{i} = [control_agents_indexes_DMPC{i}, j];
            end
        end
    end
end


%% Control Agents Matrices DMPC ADMM

control_agents_matrices_DMPC = cell(number_of_control_agents,1);
number_of_states = size(State_Nodes,2);

for k = 1:number_of_control_agents

    number_of_control_agents_Si = size(control_agents_indexes_DMPC{k},2);

    A_Si = zeros(3*number_of_control_agents_Si);
    A_Si_inter = zeros(number_of_states);
    B_Si = zeros(3*number_of_control_agents_Si,3);

    sub_index = 1;

    for i = 1:number_of_control_agents_Si
        agent_index =  control_agents_indexes_DMPC{k}(i);
        A_Si(sub_index:sub_index+2,sub_index:sub_index+2) = A((agent_index-1)*3+1:(agent_index-1)*3+3,(agent_index-1)*3+1:(agent_index-1)*3+3);
        B_Si(sub_index:sub_index+2,sub_index:sub_index+2) = B((agent_index-1)*3+1:(agent_index-1)*3+3,(agent_index-1)*3+1:(agent_index-1)*3+3);
        sub_index_interaction = 1;
        for j = 1:number_of_control_agents_Si            
            if i ~= j       
                agent_interaction_index =  control_agents_indexes_DMPC{k}(j);
                A_Si(sub_index:sub_index+2,sub_index_interaction:sub_index_interaction+2) = A((agent_index-1)*3+1:(agent_index-1)*3+3,(agent_interaction_index-1)*3+1:(agent_interaction_index-1)*3+3);
            end
            
            sub_index_interaction = sub_index_interaction + 3;
        end
        sub_index = sub_index + 3;
        A_Si_inter((agent_index-1)*3+1:(agent_index-1)*3+3,:) = A((agent_index-1)*3+1:(agent_index-1)*3+3,:);
        A_Si_inter((agent_index-1)*3+1:(agent_index-1)*3+3,(agent_index-1)*3+1:(agent_index-1)*3+3) = zeros(3);
    end
    

    control_agents_matrices_DMPC{k} = {A_Si, A_Si_inter, B_Si};

end


%% Vectors Preallocation

% State
x = zeros(3*Na,N+1);

% Input
u = zeros(3*Na,N);

% Areas Interactions
PedgeTieLine = zeros(Na,N);
PedgeTot = cell(N+1,1);

% Global cost function
JVect = zeros(1,N);

% Local cost functions
J_Si = zeros(number_of_control_agents,N);

% Time Vector
timeKeeper = zeros(1,N);
 
% Optimization Results
optResults = cell(N,1);

% Cell holding the state evolutions of individual agents
x_structure = cell(number_of_atomic_agents,1);

% Cell holding the avarage predictions for each agent z_i
consensus_structure = cell(number_of_atomic_agents,1);

% Cell holding the predicted evolutions resulting from local obptimization
% z^i
shared_evolutions = cell(number_of_control_agents,1);

% Cell holding the avarage of the predicted evolutions zbar_Si
avarage_consensus_evolutions = cell(number_of_control_agents,1);

% Gamma
gamma = cell(number_of_control_agents,1);

% Optimization Structure
optimization_problem = cell(number_of_control_agents,1);

% Time keeping structure
time_keeper = zeros(number_of_control_agents,N);

% Optimization results holder for warm start
u_result = cell(number_of_control_agents,1);

%% Initial Conditions

x(:,1) = zeros(3*Na,1);
x0 = x(:,1);

% Input
u0 = zeros(3*Na*Nu,1);
uqp = zeros(3*Na,1);

% Disturbance
w = Delta_w_forecast_inter;
 
% State and Gamma
for l = 1:number_of_control_agents
    
    number_of_control_agents_Si = size(control_agents_indexes_DMPC{l},2);
    
    x_structure{l} = zeros(3*number_of_control_agents_Si,N+1);
    gamma{l} = zeros(3*Np*number_of_control_agents_Si,1);
    u_result{l} = zeros(3*number_of_control_agents_Si*Nu,1);

    for i = 1:number_of_control_agents_Si
        avarage_consensus_evolutions{l}{i} = zeros(3*Np,1);
        shared_evolutions{l}{i} = zeros(3*Np,1);
    end

end 


%% Contruction of the optimization problems

% optimality_condition = 1e-1;
optimality_condition = 1;
% optimality_condition = 1.6;
iteration_limit = 30;

% gamma optimality
gamma_optimality = 2.5e-1;

rho = 0.1; % Consensus constant
alpha_opt = 1e2;

start_simulation_time = tic;

optimization_matrices_DMPC = cell(number_of_control_agents,1);

for k = 1:number_of_control_agents
    [Atm, Btm, Fc, Hc, Hn, d, ed, Qd, Rd, Dd, Ed, Dc] = opt_matrices_DMPC(Parameters, control_agents_indexes_DMPC{k});
    optimization_matrices_DMPC{k}{1} = Atm;
    optimization_matrices_DMPC{k}{2} = Btm;
    optimization_matrices_DMPC{k}{3} = Fc;
    optimization_matrices_DMPC{k}{4} = Hc;
    optimization_matrices_DMPC{k}{5} = Hn;
    optimization_matrices_DMPC{k}{6} = d;
    optimization_matrices_DMPC{k}{7} = ed;
    optimization_matrices_DMPC{k}{8} = Qd;
    optimization_matrices_DMPC{k}{9} = Rd;
    optimization_matrices_DMPC{k}{10} = Dd;
    optimization_matrices_DMPC{k}{11} = Ed;
    optimization_matrices_DMPC{k}{12} = Dc;
end

for l = 1:number_of_control_agents

    % Optimization matrices
    number_of_control_agents_Si = size(control_agents_indexes_DMPC{l},2);

    Atm = optimization_matrices_DMPC{l}{1};
    Btm = optimization_matrices_DMPC{l}{2};
    Fc = optimization_matrices_DMPC{l}{3};
    Hc = optimization_matrices_DMPC{l}{4};
    Hn = optimization_matrices_DMPC{l}{5};
    d = optimization_matrices_DMPC{l}{6};
    ed = optimization_matrices_DMPC{l}{7};
    Qd = optimization_matrices_DMPC{l}{8};
    Rd = optimization_matrices_DMPC{l}{9};
    Dd = optimization_matrices_DMPC{l}{10};
    Ed = optimization_matrices_DMPC{l}{11};
    Dc = optimization_matrices_DMPC{l}{12};

    optimization_problem{l}{1} = (Hc')*Qd*Hc+Rd +((rho)*eye(3*number_of_control_agents_Si*Nu));
    optimization_problem{l}{2} = Ed*Hc;

    % Bounds
    lb_Si = zeros(3*number_of_control_agents_Si,1);
    ub_Si = zeros(3*number_of_control_agents_Si,1);

    global_idx = 1;
    
    for i = 1:number_of_control_agents_Si
        agent_index =  control_agents_indexes_DMPC{l}(i);
        lb_Si(global_idx:global_idx+2,1) = lb((agent_index-1)*3+1:agent_index*3,1);
        ub_Si(global_idx:global_idx+2,1) = ub((agent_index-1)*3+1:agent_index*3,1);
        global_idx = global_idx + 3;
    end

    lb_Si_opt = zeros(3*number_of_control_agents_Si*Nu,1);
    ub_Si_opt = zeros(3*number_of_control_agents_Si*Nu,1);

    global_idx = 1;
    
    for i = 1:Nu
        lb_Si_opt(global_idx:global_idx+3*number_of_control_agents_Si-1) = lb_Si;
        ub_Si_opt(global_idx:global_idx+3*number_of_control_agents_Si-1) = ub_Si;
        global_idx=global_idx+3*number_of_control_agents_Si;
    end

    optimization_problem{l}{3} = lb_Si_opt;
    optimization_problem{l}{4} = ub_Si_opt;
end



%% Control Simulation 

idx_percentage = 0;

for k = 1:N
    
    % To display individual iterations
    if display_iterations == true
        disp(['Iteration ', num2str(k), ' of ', num2str(N)])
    end

    % % Disturburbance forecast update before optimization (Can be done After)
    % w(:,k) = Delta_w_measured_inter(:,k);

    % Perfect disturbance knowdlege
    w(:,k:k+Np) = Delta_w_measured_inter(:,k:k+Np);

    % ADMM Consensus
    iteration_counter = 1;
    
    
    norm_condition = false;
    
    norm_condition_vector = zeros(number_of_control_agents,1);
    
    % Preallocation for consensus

    for l = 1:number_of_control_agents

        number_of_control_agents_Si = size(control_agents_indexes_DMPC{l},2);

        gamma{l} = zeros(3*Np*number_of_control_agents_Si,1);

        for i = 1:number_of_control_agents_Si
            avarage_consensus_evolutions{l}{i} = zeros(3*Np,1);
            shared_evolutions{l}{i} = zeros(3*Np,1);
        end

    end 

    
    while ((iteration_counter <= iteration_limit) && ~(norm_condition))
        
        if display_iterations == true
            disp(['DMPC-ADMM iteration ', num2str(iteration_counter), ' of ', num2str(iteration_limit)])
        end
        
        % Local optimization problem for DMPC-ADMM agent Si

        % parfor l = 1:number_of_control_agents % Parallel computation
        for l = 1:number_of_control_agents
            
            start_iteration_Si = tic;
            
            number_of_control_agents_Si = size(control_agents_indexes_DMPC{l},2);
            

            % if iteration_counter == 1
                u_result{l} = zeros(3*number_of_control_agents_Si*Nu,1);
            % end


            % Initial state agent Si
            x0_Si = x_structure{l}(:,k);

            % Disturbance vector agent Si
            w_Si = zeros(2*number_of_control_agents_Si,Np);
            
            global_idx = 1;

            for i = 1:number_of_control_agents_Si
                agent_index =  control_agents_indexes_DMPC{l}(i);
                w_Si(global_idx:global_idx+1,1:Np) = w((agent_index-1)*2+1:agent_index*2,k:k+Np-1);
                global_idx = global_idx + 2;    
                
            end

            w_Si_opt = zeros(2*number_of_control_agents_Si*Np,1);
            
            global_idx = 1;

            for i = 1:Np
                w_Si_opt(global_idx:global_idx+2*number_of_control_agents_Si-1,1) = w_Si(:,i);
                global_idx=global_idx+2*number_of_control_agents_Si;
            end


            % Gamma vector
            gamma_Si = gamma{l};
            
            % Avarage consensus vectors
            zbar_Si = zeros(number_of_control_agents_Si*3*Np,1); 
            
            global_index = 1;

            for i = 1:number_of_control_agents_Si
                zbar_Si(global_index:global_index+(3*Np)-1) = avarage_consensus_evolutions{l}{i};
                global_index=global_index+(3*Np);
            end
                        
            gamma_Si_opt = zeros(number_of_control_agents_Si*3*Nu,1);
            zbar_Si_opt = zeros(number_of_control_agents_Si*3*Nu,1);
            
            global_idx1 = 1;
            global_idx2 = 1;

            if ~(k == 1 && iteration_counter == 1)
                for i = 1:Nu
                    gamma_Si_opt(global_idx1:global_idx1+(3*number_of_control_agents_Si) - 1) = gamma_Si(global_idx2:global_idx2+(3*number_of_control_agents_Si) - 1);
                    zbar_Si_opt(global_idx1:global_idx1+(3*number_of_control_agents_Si) - 1) = zbar_Si(global_idx2:global_idx2+(3*number_of_control_agents_Si) - 1);
                    
                    global_idx1 = global_idx1 + 3*number_of_control_agents_Si;
                    global_idx2 = sum(ControlSequenceDivision(1:i))*3*number_of_control_agents_Si;
                end 
            end
            
            % Optimization matrices
            Fc = optimization_matrices_DMPC{l}{3};
            Hc = optimization_matrices_DMPC{l}{4};
            
            ed = optimization_matrices_DMPC{l}{7};
            Qd = optimization_matrices_DMPC{l}{8};
            
            Ed = optimization_matrices_DMPC{l}{11};
            Dc = optimization_matrices_DMPC{l}{12};
            
            H_QP = optimization_problem{l}{1};
            f_QP = (Hc')*Qd*(Fc*x0_Si + Dc*w_Si_opt) + gamma_Si_opt - 2*rho*zbar_Si_opt;
            
            % Equality constraints
            A_QP = optimization_problem{l}{2};
            b_QP = ed - Ed*Fc*x0_Si - Ed*Dc*w_Si_opt;
            
            % % Bounds

            lb_Si_opt = optimization_problem{l}{3};
            ub_Si_opt = optimization_problem{l}{4};

            % Start Iteration Timer
            tStartIter = tic;
                
            % Gurobi
            result = Gurobi_Caller(H_QP,f_QP,A_QP,b_QP,lb_Si_opt,ub_Si_opt);
                        
            % Optimization results
            fqp_Si = result.objval;

            % Cost function update
            J_Si(l,k) = fqp_Si;

            % Storing raw result
            u_result{l} = result.x;
            
            % Local control update

            u_Si = zeros(3*number_of_control_agents_Si,Np);
                        
            % Reconstruction of the input from the blocking sequence
            global_idx1 = 1;
            global_idx2 = 1;

            for i = 1:Nu
                for j = 1:ControlSequenceDivision(i)
                    u_Si(:,global_idx1) = result.x(global_idx2:global_idx2+(3*number_of_control_agents_Si)-1,1);                   
                    global_idx1 = global_idx1 + 1;
                end

                global_idx2 = global_idx2 + (3*number_of_control_agents_Si);
            end

           
            % Shared u_Si local predicted evolution z^i
            for i = 1:number_of_control_agents_Si
                local_idx1 = (i - 1)*3 + 1;
                local_idx2 = 1;
                for j = 1:Np
                    shared_evolutions{l}{i}(local_idx2:local_idx2+2,1) = u_Si(local_idx1:local_idx1+2,j);
                    local_idx2 = local_idx2 + 3;
                end
            end
            
            % Optimality condition
            if norm(gamma_Si_opt) > gamma_optimality*max([norm(result.x(:,1)),norm(zbar_Si_opt(:,1))])
                norm_condition_vector(l,1) = 1;
            end

            end_iteration_Si = toc(start_iteration_Si);
            time_keeper(l,k) = time_keeper(l,k) + end_iteration_Si; 
        end
        

        for l = 1:number_of_control_agents
            % Global input
            number_of_local_agents_Si = size(control_agents_indexes{l},2); % this is a smaller set of agents
            
            for i = 1:number_of_local_agents_Si
                agent_index =  control_agents_indexes{l}(i);
                u((agent_index-1)*3+1:agent_index*3,k) = shared_evolutions{l}{i}(1:3,1);
            end
        end

        % Update avarage predicted evolution for individual atomic agents
        
        % Considering i
        for i = 1:number_of_atomic_agents
            number_of_shared_evolutions = 0;
            total_sum = zeros(3*Np,1);
            consensus_structure{i} = zeros(3*Np,1);

            for l = 1:number_of_control_agents
                number_of_control_agents_Si = size(control_agents_indexes_DMPC{l},2);
                for j = 1:number_of_control_agents_Si
                    if i == control_agents_indexes_DMPC{l}(j)
                        total_sum = total_sum + shared_evolutions{l}{j};
                        number_of_shared_evolutions = number_of_shared_evolutions + 1;
                    end
                end
                
            end
            
            if number_of_shared_evolutions ~= 0
                consensus_structure{i} = total_sum/number_of_shared_evolutions;
            end
        end

           
        % Reconstruct avarage predicted evolution for control agent

        for l = 1:number_of_control_agents
            number_of_control_agents_Si = size(control_agents_indexes_DMPC{l},2);
            for i = 1:number_of_control_agents_Si
                idx_evolution = control_agents_indexes_DMPC{l}(i);
                avarage_consensus_evolutions{l}{i} = consensus_structure{idx_evolution};
            end

        end

        % Update gamma
        for l = 1:number_of_control_agents
            
            number_of_control_agents_Si = size(control_agents_indexes_DMPC{l},2);

            gamma0 = gamma{l};
            
            y0 = zeros(3*number_of_control_agents_Si*Np,1);
            ybar = zeros(3*number_of_control_agents_Si*Np,1);
            
            local_idx = 1;
            for i = 1:number_of_control_agents_Si
                idx_evolution = control_agents_indexes_DMPC{l}(i);
                ybar(local_idx:local_idx+3*Np-1,1) = consensus_structure{idx_evolution};
                y0(local_idx:local_idx+3*Np-1,1) = shared_evolutions{l}{i};
                local_idx=local_idx+3*Np;
            end
            
            gamma{l} = gamma0 + rho*(y0 - ybar);

        end

        % Modified to perform at least one operation
        if iteration_counter > 1
            if sum(norm_condition_vector(:,1)) == 0
                norm_condition = true;
            end
        end
         
        % Maximum consensus deviation 
        maximum_norm = 0 ;
        for l = 1:number_of_control_agents
            number_of_control_agents_Si = size(control_agents_indexes_DMPC{l},2);
    
            gamma0 = gamma{l};
    
            y0 = zeros(3*number_of_control_agents_Si*Np,1);
            ybar = zeros(3*number_of_control_agents_Si*Np,1);
            
            local_idx = 1;
            for i = 1:number_of_control_agents_Si
                idx_evolution = control_agents_indexes_DMPC{l}(i);
            
                ybar(local_idx:local_idx+3*Np-1,1) = consensus_structure{idx_evolution};
                y0(local_idx:local_idx+3*Np-1,1) = shared_evolutions{l}{i};
                local_idx=local_idx+3*Np;
            end
    
            if norm((y0 - ybar),2) > maximum_norm
                maximum_norm = norm((y0 - ybar),2);
            end
        end

        iteration_counter = iteration_counter + 1;
       
    end
    
    % State Update
    [xplus, Pedge, PedgeTotal] = state_update_plant(x0, u(:,k), w(:,k), Parameters);
    
    j = 1;
    for h = 1:Na
        x(j,k+1) = xplus(j);
        x(j+1,k+1) = xplus(j+1);
        x(j+2,k+1) = xplus(j+2);
        j = j + 3;
    end
    x0 = x(:,k+1);

    for l = 1:number_of_control_agents
        local_idx = 1;
        number_of_control_agents_Si = size(control_agents_indexes_DMPC{l},2);
        for j = 1:number_of_control_agents_Si
            agent_idx = control_agents_indexes_DMPC{l}(j);
            x_structure{l}(local_idx:local_idx+2,k+1) = x((agent_idx-1)*3+1:agent_idx*3,k+1);
            local_idx = local_idx+3;
        end
    end

    
    % To display computation percentual, duration, expected time to complete
    if display_percentual == true
        if (k)/(N)*100 > idx_percentage
            disp(['Iteration ', num2str(k), ' of ', num2str(N), ' | Percentual = ' , num2str((k)/(N)*100), '%'])
            disp(['|Maximum consensus deviation: ', num2str(maximum_norm)])
            time_enlapsed = sum(max(time_keeper));
            total_time_enlapsed = max(time_enlapsed);
            disp(['|Total time enlapsed ', num2str(total_time_enlapsed)])
            disp(['|Expected time to complete ', num2str((total_time_enlapsed/k)*(N-k))])
            idx_percentage = idx_percentage + 1;
        end
    end

    % Cost function update
    JVect(1,k) = sum(J_Si(:,k));

end

end_simulation_time = toc(start_simulation_time);


%% Reconstruct global cost function

% Construct weighting matrices
Ac = zeros(3*number_of_atomic_agents);
Bc = zeros(3*number_of_atomic_agents);
    
Ac_Si = diag([100,10,1]);
Bc_Si = diag([1,1,1]);

for k = 1:number_of_atomic_agents
    Ac((k-1)*3+1:(k-1)*3+3,(k-1)*3+1:(k-1)*3+3) = Ac_Si;
    Bc((k-1)*3+1:(k-1)*3+3,(k-1)*3+1:(k-1)*3+3) = Bc_Si;
end


% System Parameters
DT = Parameters{2};
Kp = Parameters{10};
Tp = Parameters{11};

JVect = zeros(1,N+1);
Jsum = zeros(1,N+1);

for k = 2:N+1
    JVect(1,k) = x(:,k)'*Ac*x(:,k) + u(:,k-1)'*Bc*u(:,k-1);
    Jsum(1,k) = Jsum(1,k-1) + x(:,k)'*Ac*x(:,k) + u(:,k-1)'*Bc*u(:,k-1);
end


% total_cost = sum(JVect(1,:));
total_cost = sum(JVect);
disp(['Total cost: ', num2str(total_cost)]);
time_enlapsed = sum(max(time_keeper));
total_time_enlapsed = max(time_enlapsed);
disp(['Total time parallel: ', num2str(total_time_enlapsed)]);
disp(['Total time sequential: ', num2str(end_simulation_time)]);


%% Plot Results

PedgeTieLine = 0;

if plot_output_data == true
    plot_results(simID, export_output_plot, x, u, w, PedgeTieLine, JVect, Parameters)
end

%% Save results

if Store_Results == true
    save(['SimulationOutput/',simID]);
end

%% Support Functions


function condition = is_neighbor(control_agent_indexes_i, control_agent_index_j, A)
    
    condition = false;
    
    for i = 1:size(control_agent_indexes_i,1)
        raw_idx = (control_agent_indexes_i(i)-1)*3 + 2;
        col_idx = (control_agent_index_j-1)*3 + 1;
        if A(raw_idx,col_idx) ~= 0
            condition = true;
            return
        end
    end
   
end
