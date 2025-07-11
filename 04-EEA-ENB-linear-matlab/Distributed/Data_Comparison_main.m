clear all
close all
clc

% Figures in light theme
s = settings;
s.matlab.appearance.figure.GraphicsTheme.TemporaryValue = "light";

% To export the figures
export_figures = true;

% Simulation ID
simulation_identifier = 'Comparison_01';

%% Load P0

load('SimulationOutput/SIM_P_Atomic_Agents')

% Global variables
simulation_horizon = N;
state_nodes = State_Nodes;
input_nodes = Input_Nodes;
A_network = A; 
B_netwrok = B;

number_of_atomic_agents = Na;
atomic_agents = Atomic_Agents;
atomic_agents_matrices = Atomic_Agents_Matrices;

%% Partitioning P0

state_evolution_P0 = x;
input_evolution_P0 = u;
stage_cost_P0 = JVect;

control_agents_P0 = control_agents;
control_agents_indexes_P0 = control_agents_indexes;
control_agents_matrices_P0 = control_agents_matrices;
control_agents_DMPC_P0 = control_agents_DMPC;
control_agents_indexes_DMPC_P0 = control_agents_indexes_DMPC;
control_agents_matrices_DMPC_P0 = control_agents_indexes_DMPC;

clear x u JVect control_agents control_agents_indexes control_agents_matrices control_agents_DMPC control_agents_indexes_DMPC control_agents_indexes_DMPC

%% Partitioning P1

load('SimulationOutput/SIM_P_Opt1')

state_evolution_P1 = x;
input_evolution_P1 = u;
stage_cost_P1 = JVect;

control_agents_P1 = control_agents;
control_agents_indexes_P1 = control_agents_indexes;
control_agents_matrices_P1 = control_agents_matrices;
control_agents_DMPC_P1 = control_agents_DMPC;
control_agents_indexes_DMPC_P1 = control_agents_indexes_DMPC;
control_agents_matrices_DMPC_P1 = control_agents_indexes_DMPC;

clear x u JVect control_agents control_agents_indexes control_agents_matrices control_agents_DMPC control_agents_indexes_DMPC control_agents_indexes_DMPC

%% Partitioning P2

load('SimulationOutput/SIM_P_Opt1')

state_evolution_P2 = x;
input_evolution_P2 = u;
stage_cost_P2 = JVect;

control_agents_P2 = control_agents;
control_agents_indexes_P2 = control_agents_indexes;
control_agents_matrices_P2 = control_agents_matrices;
control_agents_DMPC_P2 = control_agents_DMPC;
control_agents_indexes_DMPC_P2 = control_agents_indexes_DMPC;
control_agents_matrices_DMPC_P2 = control_agents_indexes_DMPC;

clear x u JVect control_agents control_agents_indexes control_agents_matrices control_agents_DMPC control_agents_indexes_DMPC control_agents_indexes_DMPC

%% Partitioning P3

load('SimulationOutput/SIM_P_Geo')

state_evolution_P3 = x;
input_evolution_P3 = u;
stage_cost_P3 = JVect;

control_agents_P3 = control_agents;
control_agents_indexes_P3 = control_agents_indexes;
control_agents_matrices_P3 = control_agents_matrices;
control_agents_DMPC_P3 = control_agents_DMPC;
control_agents_indexes_DMPC_P3 = control_agents_indexes_DMPC;
control_agents_matrices_DMPC_P3 = control_agents_indexes_DMPC;

clear x u JVect control_agents control_agents_indexes control_agents_matrices control_agents_DMPC control_agents_indexes_DMPC control_agents_indexes_DMPC


%% Partitioning P4

load('SimulationOutput/SIM_P_Rnd')

state_evolution_P4 = x;
input_evolution_P4 = u;
stage_cost_P4 = JVect;

control_agents_P4 = control_agents;
control_agents_indexes_P4 = control_agents_indexes;
control_agents_matrices_P4 = control_agents_matrices;
control_agents_DMPC_P4 = control_agents_DMPC;
control_agents_indexes_DMPC_P4 = control_agents_indexes_DMPC;
control_agents_matrices_DMPC_P4 = control_agents_indexes_DMPC;

clear x u JVect control_agents control_agents_indexes control_agents_matrices control_agents_DMPC control_agents_indexes_DMPC control_agents_indexes_DMPC

%% Data Comparison

state_norm_evolution_P0 = zeros(3,simulation_horizon+1);
state_norm_evolution_P1 = zeros(3,simulation_horizon+1);
state_norm_evolution_P2 = zeros(3,simulation_horizon+1);
state_norm_evolution_P3 = zeros(3,simulation_horizon+1);
state_norm_evolution_P4 = zeros(3,simulation_horizon+1);

for k = 1:simulation_horizon+1
    for i = 1:3
        state_norm_evolution_P0(i,k) = norm(state_evolution_P0(i:3:end,k));
        state_norm_evolution_P1(i,k) = norm(state_evolution_P1(i:3:end,k));
        state_norm_evolution_P2(i,k) = norm(state_evolution_P2(i:3:end,k));
        state_norm_evolution_P3(i,k) = norm(state_evolution_P3(i:3:end,k));
        state_norm_evolution_P4(i,k) = norm(state_evolution_P4(i:3:end,k));
    end
end

input_norm_evolution_P0 = zeros(1,simulation_horizon);
input_norm_evolution_P1 = zeros(1,simulation_horizon);
input_norm_evolution_P2 = zeros(1,simulation_horizon);
input_norm_evolution_P3 = zeros(1,simulation_horizon);
input_norm_evolution_P4 = zeros(1,simulation_horizon);

for k = 1:simulation_horizon
    for i = 1:3
        input_norm_evolution_P0(i,k) = norm(input_evolution_P0(i:3:end,k));
        input_norm_evolution_P1(i,k) = norm(input_evolution_P1(i:3:end,k));
        input_norm_evolution_P2(i,k) = norm(input_evolution_P2(i:3:end,k));
        input_norm_evolution_P3(i,k) = norm(input_evolution_P3(i:3:end,k));
        input_norm_evolution_P4(i,k) = norm(input_evolution_P4(i:3:end,k));
    end
end

%% Figures

%% State x_1 norm plot
f1 = figure('visible','on');
f1.Position = [100 100 1380 820];
xlim([0 N])

grid on
hold on

stairs(0:N,state_norm_evolution_P0(1,:),'-','LineWidth',3)
stairs(0:N,state_norm_evolution_P1(1,:),'--','LineWidth',3)
stairs(0:N,state_norm_evolution_P2(1,:),'-.','LineWidth',3)
stairs(0:N,state_norm_evolution_P3(1,:),'-','LineWidth',3)
stairs(0:N,state_norm_evolution_P4(1,:),'--','LineWidth',3)

tit = title('$\Delta \delta(k)$: Power angle deviation','Interpreter','latex');
lgd = legend({'Partitioning $\mathcal{P}_{\textrm{DMPC}}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},1}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},2}$', 'Partitioning $\mathcal{P}_{\textrm{Geo}}$', 'Partitioning $\mathcal{P}_{\textrm{Rnd}}$'},'Interpreter','latex','Location','southeast');

xlab = xlabel('Time step','Interpreter','latex');
ylab = ylabel('Deg','Interpreter','latex');

ax = gca;
ax.YAxis.Exponent = 0;
    
set(f1.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
tit.FontSize = 20*2;
xlab.FontSize = 18*2;
ylab.FontSize = 18*2;
leg.FontSize = 14*2;
f1.CurrentAxes.Box = 'on';

hold off


%% State x_2 norm plot
f2 = figure('visible','on');
f2.Position = [100 100 1380 820];
xlim([0 N])

grid on
hold on

stairs(0:N,state_norm_evolution_P0(2,:),'-','LineWidth',3)
stairs(0:N,state_norm_evolution_P1(2,:),'--','LineWidth',3)
stairs(0:N,state_norm_evolution_P2(2,:),'-.','LineWidth',3)
stairs(0:N,state_norm_evolution_P3(2,:),'-','LineWidth',3)
stairs(0:N,state_norm_evolution_P4(2,:),'--','LineWidth',3)

tit = title('$\Delta f(k)$: Frequency deviation','Interpreter','latex');
lgd = legend({'Partitioning $\mathcal{P}_{\textrm{DMPC}}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},1}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},2}$', 'Partitioning $\mathcal{P}_{\textrm{Geo}}$', 'Partitioning $\mathcal{P}_{\textrm{Rnd}}$'},'Interpreter','latex','Location','northeast');

xlab = xlabel('Time step','Interpreter','latex');
ylab = ylabel('Hz','Interpreter','latex');

ax = gca;
ax.YAxis.Exponent = 0;
    
set(f2.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
tit.FontSize = 20*2;
xlab.FontSize = 18*2;
ylab.FontSize = 18*2;
leg.FontSize = 14*2;
f2.CurrentAxes.Box = 'on';

hold off

%% State x_3 norm plot
f3 = figure('visible','on');
f3.Position = [100 100 1380 820];
xlim([0 N])

grid on
hold on

stairs(0:N,state_norm_evolution_P0(3,:),'-','LineWidth',3)
stairs(0:N,state_norm_evolution_P1(3,:),'--','LineWidth',3)
stairs(0:N,state_norm_evolution_P2(3,:),'-.','LineWidth',3)
stairs(0:N,state_norm_evolution_P3(3,:),'-','LineWidth',3)
stairs(0:N,state_norm_evolution_P4(3,:),'--','LineWidth',3)

tit = title('$e(k)$: Energy stored','Interpreter','latex');
lgd = legend({'Partitioning $\mathcal{P}_{\textrm{DMPC}}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},1}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},2}$', 'Partitioning $\mathcal{P}_{\textrm{Geo}}$', 'Partitioning $\mathcal{P}_{\textrm{Rnd}}$'},'Interpreter','latex','Location','southeast');

xlab = xlabel('Time step','Interpreter','latex');
ylab = ylabel('GWh','Interpreter','latex');

ax = gca;
ax.YAxis.Exponent = 0;
    
set(f3.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
tit.FontSize = 20*2;
xlab.FontSize = 18*2;
ylab.FontSize = 18*2;
leg.FontSize = 14*2;
f3.CurrentAxes.Box = 'on';

hold off

%% Input u_1 norm plot
f4 = figure('visible','on');
f4.Position = [100 100 1380 820];
xlim([0 N])

grid on
hold on

stairs(0:N-1,input_norm_evolution_P0(1,:),'-','LineWidth',3)
stairs(0:N-1,input_norm_evolution_P1(1,:),'--','LineWidth',3)
stairs(0:N-1,input_norm_evolution_P2(1,:),'-.','LineWidth',3)
stairs(0:N-1,input_norm_evolution_P3(1,:),'-','LineWidth',3)
stairs(0:N-1,input_norm_evolution_P4(1,:),'--','LineWidth',3)

tit = title('$\Delta P^{disp}(k)$:  Dispatchable generation variation','Interpreter','latex');
lgd = legend({'Partitioning $\mathcal{P}_{\textrm{DMPC}}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},1}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},2}$', 'Partitioning $\mathcal{P}_{\textrm{Geo}}$', 'Partitioning $\mathcal{P}_{\textrm{Rnd}}$'},'Interpreter','latex','Location','southeast');

xlab = xlabel('Time step','Interpreter','latex');
ylab = ylabel('GW','Interpreter','latex');

ax = gca;
ax.YAxis.Exponent = 0;
    
set(f4.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
tit.FontSize = 20*2;
xlab.FontSize = 18*2;
ylab.FontSize = 18*2;
leg.FontSize = 14*2;
f4.CurrentAxes.Box = 'on';

hold off

%% Input u_2 norm plot
f5 = figure('visible','on');
f5.Position = [100 100 1380 820];
xlim([0 N])

grid on
hold on

stairs(0:N-1,input_norm_evolution_P0(2,:),'-','LineWidth',3)
stairs(0:N-1,input_norm_evolution_P1(2,:),'--','LineWidth',3)
stairs(0:N-1,input_norm_evolution_P2(2,:),'-.','LineWidth',3)
stairs(0:N-1,input_norm_evolution_P3(2,:),'-','LineWidth',3)
stairs(0:N-1,input_norm_evolution_P4(2,:),'--','LineWidth',3)

tit = title('$P^{ESS,c}(k)$: Energy storage charging power','Interpreter','latex');
lgd = legend({'Partitioning $\mathcal{P}_{\textrm{DMPC}}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},1}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},2}$', 'Partitioning $\mathcal{P}_{\textrm{Geo}}$', 'Partitioning $\mathcal{P}_{\textrm{Rnd}}$'},'Interpreter','latex','Location','southeast');

xlab = xlabel('Time step','Interpreter','latex');
ylab = ylabel('GW','Interpreter','latex');

ax = gca;
ax.YAxis.Exponent = 0;
    
set(f5.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
tit.FontSize = 20*2;
xlab.FontSize = 18*2;
ylab.FontSize = 18*2;
leg.FontSize = 14*2;
f5.CurrentAxes.Box = 'on';

%% Input u_3 norm plot
f6 = figure('visible','on');
f6.Position = [100 100 1380 820];
xlim([0 N])

grid on
hold on

stairs(0:N-1,input_norm_evolution_P0(3,:),'-','LineWidth',3)
stairs(0:N-1,input_norm_evolution_P1(3,:),'--','LineWidth',3)
stairs(0:N-1,input_norm_evolution_P2(3,:),'-.','LineWidth',3)
stairs(0:N-1,input_norm_evolution_P3(3,:),'-','LineWidth',3)
stairs(0:N-1,input_norm_evolution_P4(3,:),'--','LineWidth',3)

tit = title('$P^{ESS, d}(k)$: Energy storage discharging power','Interpreter','latex');
lgd = legend({'Partitioning $\mathcal{P}_{\textrm{DMPC}}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},1}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},2}$', 'Partitioning $\mathcal{P}_{\textrm{Geo}}$', 'Partitioning $\mathcal{P}_{\textrm{Rnd}}$'},'Interpreter','latex','Location','southeast');

xlab = xlabel('Time step','Interpreter','latex');
ylab = ylabel('GW','Interpreter','latex');

ax = gca;
ax.YAxis.Exponent = 0;
    
set(f6.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
tit.FontSize = 20*2;
xlab.FontSize = 18*2;
ylab.FontSize = 18*2;
leg.FontSize = 14*2;
f6.CurrentAxes.Box = 'on';
hold off

%% State cost comparison
f7 = figure('visible','on');
f7.Position = [100 100 1380 820];
xlim([0 N])

grid on
hold on

stairs(0:N,stage_cost_P0(1,:),'-','LineWidth',3)
stairs(0:N,stage_cost_P1(1,:),'--','LineWidth',3)
stairs(0:N,stage_cost_P2(1,:),'-.','LineWidth',3)
stairs(0:N,stage_cost_P3(1,:),'-','LineWidth',3)
stairs(0:N,stage_cost_P4(1,:),'--','LineWidth',3)

tit = title('Stage cost $L(x,u,k)$','Interpreter','latex');
lgd = legend({'Partitioning $\mathcal{P}_{\textrm{DMPC}}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},1}$', 'Partitioning $\mathcal{P}_{\textrm{Opt},2}$', 'Partitioning $\mathcal{P}_{\textrm{Geo}}$', 'Partitioning $\mathcal{P}_{\textrm{Rnd}}$'},'Interpreter','latex','Location','southeast');

xlab = xlabel('Time step','Interpreter','latex');
% ylab = ylabel('GW','Interpreter','latex');

ax = gca;
ax.YAxis.Exponent = 0;
    
set(f7.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
tit.FontSize = 20*2;
xlab.FontSize = 18*2;
% ylab.FontSize = 18*2;
leg.FontSize = 14*2;
f7.CurrentAxes.Box = 'on';
hold off


%% Export graphics

if export_figures == true
    exportgraphics(f1,['SimulationOutput/',simulation_identifier,'_X1Norm.pdf'],'Resolution',300)
    exportgraphics(f2,['SimulationOutput/',simulation_identifier,'_X2Norm.pdf'],'Resolution',300)
    exportgraphics(f3,['SimulationOutput/',simulation_identifier,'_X3Norm.pdf'],'Resolution',300)
    exportgraphics(f4,['SimulationOutput/',simulation_identifier,'_U1Norm.pdf'],'Resolution',300)
    exportgraphics(f5,['SimulationOutput/',simulation_identifier,'_U2Norm.pdf'],'Resolution',300)
    exportgraphics(f6,['SimulationOutput/',simulation_identifier,'_U3Norm.pdf'],'Resolution',300)
    exportgraphics(f7,['SimulationOutput/',simulation_identifier,'_Cost.pdf'],'Resolution',300)
end