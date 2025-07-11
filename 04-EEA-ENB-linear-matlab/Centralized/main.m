clearvars
clc
close all

% For notation
format shortE 

% Simulation Name
simID = 'SIM_ID';

%% Simulation Options

% Input Data Plot and Export
plot_input_data = false;
export_input_plot = false;

% Output Data Plot and Export
plot_output_data = true;
export_output_plot = false;
export_results = false;


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


%% Solver Parameters

ConsTol = 1e-6;
OptTol = 1e-6;


%% Vectors Preallocation

% State
x = zeros(5*Na,N+1);

% Input
u = zeros(3*Na,N);

% Areas Interactions
PedgeTieLine = zeros(Na,N);
PedgeTot = cell(N+1,1);

% Cost Function
JVect = zeros(1,N);

% Time Vector
timeKeeper = zeros(N,1);
 
% Optimization Results
optResults = cell(N,1);


%% Optimization Matrices

[Atm, Btm, Fc, Hc, Hn, d, ed, Qd, Rd, Dd, Ed, Dc] = opt_matrices(Parameters);


H_QP = (Hc')*Qd*Hc+Rd; 
% To avoid numeriacal issues with quadprog
% H_QP = (H_QP+H_QP')/2;

A_QP = Ed*Hc;


%% Initial Conditions

% State ensuring load matching at zero
k = 1;
for i = 4:5:5*Na
    x(i,1) = Pdisp_zero(k,1);
    k = k  + 1;
end
x0 = x(:,1);

% Input
u0 = zeros(3*Na*Nu,1);
uqp = zeros(2*Na,1);

% Disturbance
w = Delta_w_forecast_inter;

%% MPC

display_iterations = false;
display_percentual = true;

% Start MPC Timer
tStart = tic; 

idxPer = 0;


for k = 1:N
    
    % To display individual iterations
    if display_iterations == true
        disp(['Iteration ', num2str(k), ' of ', num2str(N)])
    end

    % Disturburbance forecast update before optimization (Can be done After)
    w(:,k) = Delta_w_measured_inter(:,k);

    % Disturburbance forecast update before optimization  (Alternative)
    % w(:,h:h+Np) = Delta_w_measured_inter(:,h:h+Np);

    % Disturbance vector for optimization
    wbar = zeros(Np*2*Na,1);
    for i = 1:Np
        wbar((i-1)*2*Na+1:i*2*Na,1) = w(:,k+i-1);
    end
           
    % Start Iteration Timer
    tStartIter = tic;
        
    % Optimization Matrices
    f_QP = (Hc')*Qd*(Fc*x0 + Dc*wbar);
    b_QP = ed - Ed*Fc*x0 - Ed*Dc*wbar;

    % If disturbance is not considered
    % f_QP = (Hc')*Qd*Fc*x0;
    % b_QP = ed - Ed*Fc*x0;

    % beq_QP = zeros(NumEq,1);
    % optionsQP = optimoptions('quadprog','Display','final','Algorithm','interior-point-convex');

    % QuadProg
    % optionsQP = optimoptions('quadprog','Display','none','Algorithm','interior-point-convex');
    % [uqp,fqp,exitflag,output] = quadprog(H_QP,f_QP,A_QP,b_QP,[],[],lb,ub,u0,optionsQP);
    % optResults{k} = [uqp,fqp,exitflag,output];
    % u0 = [uqp((3*Na)+1:end,1);uqp(3*Na*(Nu-1)+1:end,1)];

    % Gurobi
    result = GurobiCaller(H_QP,f_QP,A_QP,b_QP,lb,ub);
    optResults{k} = result;
    for i = 1:3*Na
        uqp(i,1) = result.x(i);
    end
    fqp = result.objval;

    % Stop Iteration Timer
    tEndIter = toc(tStartIter);
    timeKeeper(k,1) = tEndIter;
      
    % Cost Function Store
    JVect(1,k) = fqp;

    % Disturburbance forecast update after optimization 
    % w(:,h) = Delta_w_measured_inter(:,h);

    % Input Store
    j = 1;
    for h = 1:Na
        u(j,k) = uqp(j,1);
        u(j+1,k) = uqp(j+1,1);
        u(j+2,k) = uqp(j+2,1);
        j = j + 3;
    end    

    % State Update
    [xplus, Pedge, PedgeTotal] = state_update_plant(x0, uqp(1:3*Na,1), w(:,k), Parameters);
    
    j = 1;
    for h = 1:Na
        x(j,k+1) = xplus(j);
        x(j+1,k+1) = xplus(j+1);
        x(j+2,k+1) = xplus(j+2);
        x(j+3,k+1) = xplus(j+3);
        x(j+4,k+1) = xplus(j+4);
        j = j + 5;
    end
    x0 = x(:,k+1);
    
    % Areas Interaction Store
    PedgeTot{k} = Pedge;
    PedgeTieLine(:,k) = PedgeTotal;
            
    % To display computation percentual, duration, expected time to complete
    if display_percentual == true
        if (k)/(N)*100 > idxPer
            disp(['Iteration ', num2str(k), ' of ', num2str(N), ' | Percentual = ' , num2str((k)/(N)*100), '%'])
            disp(['|Total time enlapsed ', num2str(sum(timeKeeper))])
            disp(['|Expected time to complete ', num2str((sum(timeKeeper)/k)*(N-k))])
            idxPer = idxPer + 2;
        end
    end
end

% Stop MPC Timer
tEnd = toc(tStart); 

disp(['Computation complete. Execution time = ', num2str(tEnd), ' [s]'])


%% Results Export

if export_results == true
    GW = 0;
    
    for i = 1:27
        if ismember(i,CountryCodes) 
            GW = GW + CapacitiesData(1,i)/1000;
        end
    end
    GW = floor(GW);
    
    filenameWorkspace = ['SimulationOutput/',simID, '_Workspace_',num2str(Na),'Areas_',num2str(GW),'GW'];
    save(filenameWorkspace,'simID','Parameters','x','u','w','PedgeTieLine','JVect','tStart','tEnd','timeKeeper','optResults','w_mesured_inter','w_forecast_inter','Pdisp_zero','Delta_w_measured_inter','Delta_w_forecast_inter');
end


%% Plots

if plot_output_data == true
    plot_results(simID, export_output_plot, x, u, w, PedgeTieLine, JVect, Parameters)
end
