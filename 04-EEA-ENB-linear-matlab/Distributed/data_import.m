function [Parameters, w_measured_inter, w_forecast_inter, Pdisp_zero, Delta_w_measured_inter, Delta_w_forecast_inter] = data_import(simID, plot_input_data, export_input_plot)    
%% Simulation Parameters
    
    % Cell Array cointaining all the parameters for the simulation
    Parameters = cell(0);
    
    % Select which countries will be used for simulation
    % Some countries
    % CountryCodes = [9,10,14,26,13,17];
    % All countries
    CountryCodes = 1:26;
    CountryCodes = sort(CountryCodes);
    Parameters{1} = CountryCodes;
    % Number of electrical areas
    Na = size(CountryCodes,2);
    Parameters{7} = Na;


    % Select the control sequence structure for blocking
    % ControlSequenceDivision = [1;1;1;1;1];
    ControlSequenceDivision = [1;1;1;1;1;10;15];
    Parameters{29} = ControlSequenceDivision;

    % Compute the prediction horizon
    Np = sum(ControlSequenceDivision); %[steps]
    Parameters{8} = Np;

    % Number of steps each hour
    IterationSegments = 60;
    % IterationSegments = 1440;
    Parameters{4} = IterationSegments;

    % Hours of simulations
    DataIntervals = 1;
    % DataIntervals = 24;     
    SimulationSteps = DataIntervals*IterationSegments;
    Parameters{3} = SimulationSteps;
    % Duration of the Simulation
    N = SimulationSteps;
    Parameters{9} = N;
    
    % SamplingTime
    SamplingTime = 2.5;       %[s]
    Parameters{2} = SamplingTime;
    
    % Constraints on the electrical machines states
    PowerAngleLimit = 30;
    % FOR DMPC
    % PowerAngleLimit = 2;
    Parameters{5} = PowerAngleLimit;
    FrequencyLimit = 0.04;
    % FOR DMPC
    % FrequencyLimit = 0.03;
    Parameters{6} = FrequencyLimit;
    

%%  Electrical areas parameters

    % Gain of the elctrical machines
    Kp = 0.05*ones(Na,1);
    Parameters{10} = Kp;
    % Time constant of the elctrical machines
    Tp = 25*ones(Na,1);
    Parameters{11} = Tp;
    % Charging rate of the ESSs
    nc = 0.9*ones(Na,1);
    Parameters{12} = nc;
    % Discharging rate of the ESSs
    nd = 1.1*ones(Na,1);
    Parameters{13} = nd;
    % ESSs parameters used for contraints
    BatteryPowerScaling = 1;
    Parameters{14} = BatteryPowerScaling;
    BatteryCapacityScaling = SamplingTime;
    Parameters{15} = BatteryCapacityScaling;
 
    
%%  Optimization Parameters

    % Number of control variable vectors
    % Nu = size(ControlSequenceDivision,1);
    % Optimization matrices
    Ac = zeros(3*Na);
    Bc = zeros(3*Na);
    % Used to extend the cost function
    Ec = zeros(3*Na);
    

    for i = 1:Na
        Ac(3*(i-1)+1:3*(i-1)+3,3*(i-1)+1:3*(i-1)+3) = [100 0 0; 0 10 0; 0 0 1];
        Bc(3*(i-1)+1:3*(i-1)+3,3*(i-1)+1:3*(i-1)+3) = [1 0 0; 0 1 0; 0 0 1];
        Ec(3*(i-1)+1:3*(i-1)+3,3*(i-1)+1:3*(i-1)+3) = [0 0 0; 0 0 0; 0 0 0];
    end
   
   % Used to extend the cost function 
   KPtie = 0; 
    
   Parameters{16} = Ac;
   Parameters{17} = Bc;
   Parameters{18} = Ec;
   Parameters{19} = KPtie;


    %% Country ISO Labels
        
    CISO = ['AT';'BE';'BG';'HR';'CZ';'DK';'EE';'FI';'FR';'DE';'GR';'HU';'IE';'IT';'LV';'LT';'NL';'NO';'PL';'PT';'RO';'SK';'SI';'ES';'SE';'CH'];
    
    % Country Label vector involved
    CISO_Import = '';
    k = 1;
    
    for i = 1:26
        if max(CountryCodes == i)
            CISO_Import(k,:) = CISO(i,:);
            k = k + 1;
        end
    end
    
    Parameters{25} = CISO_Import;


    %% Geographical coordinates
    
    Centroids = readmatrix("Data/Centroids.csv");
    
    CentoidPositions = zeros(Na,2);
    for i = 1:Na
            CentoidPositions(i,1:2) = Centroids(CountryCodes(i),3:4);
    end
    Parameters{20} = CentoidPositions;

    
    %% Electrical topology data
    
    AdjacencyData = readmatrix("Data/Adjacency_Matrix.csv");
    
    % Adjacency matrix preallocation
    A = zeros(Na);
    
    % Build Adjacency Matrix
    k = 1;
    
    for i = 1:26
        if max(CountryCodes == i)     
            for j = 3:size(AdjacencyData,2)
                if max(AdjacencyData(i,j) == CountryCodes) == 1        
                    idx = AdjacencyData(i,j) == CountryCodes;
                    A(k,idx) = 1;               
                end
            end
            k = k + 1;       
        end
    end
    Parameters{21} = A;
    
    % Weighting matrix preallocation
    AW = zeros(Na);
    % Build Weighting Matrix
    for i=1:Na
        for j=1:Na
            if A(i,j) == 1
                AW(i,j) = sqrt(((CentoidPositions(j,1)-CentoidPositions(i,1))^2)+((CentoidPositions(j,2)-CentoidPositions(i,2))^2));
            end
        end
    end
    Parameters{22} = AW;

    % Avarage Distance
    NumOfEdges = sum(sum(A));
    DistanceSum = sum(sum(AW));
    DAvg = DistanceSum/NumOfEdges;
    Parameters{28} = DAvg;
    % KLine = DAvg;
    KLine = 1;
    Parameters{27} = KLine;


    %% Dipatchable sources and battery capacities limitis
    
    % Import Capacities data
    CapacitiesData = readmatrix("Data/Capacities.csv");
    % We increase the maximum dispatchable capacity by 10% 
    CapacitiesData = 1.1*CapacitiesData(:,3)'; 
    Parameters{26} = CapacitiesData;

    % Capacities Preallocation 
    AreaLimits = zeros(2,2*size(CountryCodes,2));
    
    k = 1;
    for i = 1:26
        if max(CountryCodes == i) 
            AreaLimits(1,k:k+2) = [-CapacitiesData(1,i)/(SamplingTime),0,0]/1000;
            AreaLimits(2,k:k+2) = [CapacitiesData(1,i)/(SamplingTime),CapacitiesData(1,i)/(SamplingTime), ...
                                                                      CapacitiesData(1,i)/(SamplingTime)]/1000;
            k = k + 3; 
        end
    end
    
    % Lower bound and upper bound vectors for simulation
    LowerBound = [];
    UpperBound = [];
    
    % Number of control variable vectors
    Nu = size(ControlSequenceDivision,1);
    
    % Control bounds
    for i = 1:Nu
        LowerBound = cat(2,LowerBound,AreaLimits(1,:));
        UpperBound = cat(2,UpperBound,AreaLimits(2,:));
    end
    Parameters{23} = LowerBound;
    Parameters{24} = UpperBound;
    

    %% Data Import
    
    % External Preallocation
    w_forecast = cell(Na,1);
    w_measured = cell(Na,1);
    
    % Vector Preallocation
    k = 1;
    
    for i = 1:Na
        if CountryCodes(i) < 10
            dataread = readmatrix(['Data/','0',num2str(CountryCodes(i)),'_Aggregated.csv'])';
        else
            dataread = readmatrix(['Data/',num2str(CountryCodes(i)),'_Aggregated.csv'])';
        end
        
        % To consider data every 15 minutes
        % w_forecast{i} = [dataread(1,:);dataread(3,:)]/1000;
        % w_measured{i} = [dataread(2,:);dataread(4,:)]/1000;
        % To consider data every hour 
        w_forecast{i} = [dataread(1,1:4:end);dataread(3,1:4:end)]/1000;
        w_measured{i} = [dataread(2,1:4:end);dataread(4,1:4:end)]/1000;
        
        k = k + 2;
    end
    
    
    %% Initial Conditions

    Pdisp_zero = zeros(Na,1);
    w_zero = zeros(2*Na,1);
    k = 1;
    for i = 1:Na
        Pdisp_zero(i,1) = max(w_measured{i}(1,1) - w_measured{i}(2,1),0);
        w_zero(k,1) = w_measured{i}(1,1);
        w_zero(k+1,1) = w_measured{i}(2,1);
        k = k + 2;
    end


    %% Data Interpolation
    
    DataIntervalsCounter = 1;
    DataIntCountIdx = 0;
    w_measured_inter = zeros(2*Na,N+Np);
    Delta_w_measured_inter = zeros(2*Na,N+Np);
    Delta_w_forecast_inter = zeros(2*Na,N+Np);
    w_forecast_inter = zeros(2*Na,N+Np);

    for h = 1:N+Np
        
        if h == DataIntervalsCounter 
            DataIntervalsCounter = DataIntervalsCounter + IterationSegments;
            DataIntCountIdx = DataIntCountIdx + 1;
        end
        k = 1;
        for m = 1:Na
            if h == 1
                w_measured_inter(k:k+1,h) = [w_measured{m}(1,1);w_measured{m}(2,1)];
                w_forecast_inter(k:k+1,h) = [w_forecast{m}(1,1);w_forecast{m}(2,1)];
                Delta_w_measured_inter(k:k+1,h) = ((w_measured{m}(:,DataIntCountIdx+1)-w_measured{m}(:,DataIntCountIdx))/(IterationSegments))/SamplingTime;
                Delta_w_forecast_inter(k:k+1,h) = ((w_forecast{m}(:,DataIntCountIdx+1)-w_forecast{m}(:,DataIntCountIdx))/(IterationSegments))/SamplingTime;
                k = k + 2; 
            else
                w_measured_inter(k:k+1,h) = w_measured_inter(k:k+1,h-1) + ((w_measured{m}(:,DataIntCountIdx+1)-w_measured{m}(:,DataIntCountIdx))/(IterationSegments)); 
                w_forecast_inter(k:k+1,h) = w_forecast_inter(k:k+1,h-1) + ((w_forecast{m}(:,DataIntCountIdx+1)-w_forecast{m}(:,DataIntCountIdx))/(IterationSegments));   
                Delta_w_measured_inter(k:k+1,h) = ((w_measured{m}(:,DataIntCountIdx+1)-w_measured{m}(:,DataIntCountIdx))/(IterationSegments))/SamplingTime;
                Delta_w_forecast_inter(k:k+1,h) = ((w_forecast{m}(:,DataIntCountIdx+1)-w_forecast{m}(:,DataIntCountIdx))/(IterationSegments))/SamplingTime;
                k = k + 2; 
            end
        end
    end 
    
    % Closing condition for the termination of the algorithm.
    
    vector_raws = size(w_measured_inter,1);
    
    for i = N:N+Np
        for j = 1:vector_raws
            w_measured_inter(j,i) = w_measured_inter(j,N);
            w_forecast_inter(j,i) = w_forecast_inter(j,N);
            Delta_w_measured_inter(j,i) = Delta_w_measured_inter(j,N);
            Delta_w_forecast_inter(j,i) = Delta_w_forecast_inter(j,N);
        end
    end

       


%% Input Data Plot
    if plot_input_data == true

    % Color Map
        plotColors = jet(Na);
    


    % Labels Legend

        labels = char(zeros(Na, 9));
        for i = 1:Na
            if CountryCodes(i) < 10
                labels(i,:) = ['0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
            else
                labels(i,:) = [num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
            end
        end
    
    print_labels = false;

    % Measured Load Curve (w_1)
    
        f1 = figure('visible','on');
        f1.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(w_measured_inter(1:2:end,1:end))) 1.05*max(max(w_measured_inter(1:2:end,1:end)))])
        grid on
        hold on
        k = 1;
        for i = 1:2:2*Na
            stairs(0:N,w_measured_inter(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        tit = title('Measured Load Curve','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments:N);
        xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        ax = gca;
        ax.YAxis.Exponent = 0;
        
        if print_labels == true
            leg = legend(labels,'Location','eastoutside','Interpreter','latex');
            leg.FontSize = 14*2;
        end

        set(f1.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f1.CurrentAxes.Box = 'on';
    
        hold off
    

    % Measured Renewabble Generation (w_2)
    
        f2 = figure('visible','on');
        f2.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(w_measured_inter(2:2:end,1:end))) 1.05*max(max(w_measured_inter(2:2:end,1:end)))])
        grid on
        hold on
        k = 1;
        for i = 2:2:2*Na
            stairs(0:N,w_measured_inter(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        tit = title('Measured Renewable Generation','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments:N);
        xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        ax = gca;
        ax.YAxis.Exponent = 0;
        if print_labels == true
            leg = legend(labels,'Location','eastoutside','Interpreter','latex');
            leg.FontSize = 14*2;
        end

        set(f2.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f2.CurrentAxes.Box = 'on';
    
        hold off
  

    % Forecast of Load Curve (w_1)
    
        f3 = figure('visible','on');
        f3.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(w_forecast_inter(1:2:end,1:end))) 1.05*max(max(w_forecast_inter(1:2:end,1:end)))])
        grid on
        hold on
        k = 1;
        for i = 1:2:2*Na
            stairs(0:N,w_forecast_inter(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        tit = title('Forecast of Load Curve','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments:N);
        xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        ax = gca;
        ax.YAxis.Exponent = 0;
        % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
        % leg.FontSize = 14*2;

        set(f3.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f3.CurrentAxes.Box = 'on';
    
        hold off
  

    % Forecast of Renewabble Generation (w_2)
    
        f4 = figure('visible','on');
        f4.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(w_forecast_inter(2:2:end,1:end))) 1.05*max(max(w_forecast_inter(2:2:end,1:end)))])
        grid on
        hold on
        k = 1;
        for i = 2:2:2*Na
            stairs(0:N,w_forecast_inter(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        tit = title('Forecast of Renewable Generation','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments:N);
        xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        ax = gca;
        ax.YAxis.Exponent = 0;
        % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
        % leg.FontSize = 14*2;

        set(f4.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f4.CurrentAxes.Box = 'on';
    
        hold off
 

    % w1 -- Measured Load Curve Increments 
    
        f5 = figure('visible','on');
        f5.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(Delta_w_measured_inter(1:2:end,1:end))) 1.05*max(max(Delta_w_measured_inter(1:2:end,1:end)))])
        grid on
        hold on
        k = 1;
        for i = 1:2:2*Na
            stairs(0:N,Delta_w_measured_inter(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        tit = title('$w_1$ -- Measured Load Curve Increments','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments:N);
        xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        ax = gca;
        ax.YAxis.Exponent = 0;
        % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
        % leg.FontSize = 14*2;

        set(f5.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f5.CurrentAxes.Box = 'on';
    
        hold off


    % w2 -- Measured Renewabble Generation Increments
    
        f6 = figure('visible','on');
        f6.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(Delta_w_measured_inter(2:2:end,1:end))) 1.05*max(max(Delta_w_measured_inter(2:2:end,1:end)))])
        grid on
        hold on
        k = 1;
        for i = 2:2:2*Na
            stairs(0:N,Delta_w_measured_inter(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        tit = title('$w_2$ -- Measured Renewable Generation Increments','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments:N);
        xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        ax = gca;
        ax.YAxis.Exponent = 0;
        % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
        % leg.FontSize = 14*2;

        set(f6.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f6.CurrentAxes.Box = 'on';
    
        hold off
    
    
    % w1 -- Forecast of Load Curve
    
        f7 = figure('visible','on');
        f7.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(Delta_w_forecast_inter(1:2:end,1:end))) 1.05*max(max(Delta_w_forecast_inter(1:2:end,1:end)))])
        grid on
        hold on
        k = 1;
        for i = 1:2:2*Na
            stairs(0:N,Delta_w_forecast_inter(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        tit = title('$w_1$ -- Forecast of Load Curve Increments','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments:N);
        xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        ax = gca;
        ax.YAxis.Exponent = 0;
        % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
        % leg.FontSize = 14*2;

        set(f7.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f7.CurrentAxes.Box = 'on';
    
        hold off
    

    % w2 -- Forecast of Renewabble Generation Increments
    
        f8 = figure('visible','on');
        f8.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(Delta_w_forecast_inter(2:2:end,1:end))) 1.05*max(max(Delta_w_forecast_inter(2:2:end,1:end)))])
        grid on
        hold on
        k = 1;
        for i = 2:2:2*Na
            stairs(0:N,Delta_w_forecast_inter(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        tit = title('$w_2$ -- Forecast of Renewable Generation Increments','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments:N);
        xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        ax = gca;
        ax.YAxis.Exponent = 0;
        % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
        % leg.FontSize = 14*2;

        set(f8.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f8.CurrentAxes.Box = 'on';
    
        hold off    
        
    end


%% Export Graphic

if export_input_plot == true

        exportgraphics(f1,['SimulationOutput/',simID,'_MeasuredLoad.pdf'],'Resolution',300)
        exportgraphics(f2,['SimulationOutput/',simID,'_MeasuredRenewable.pdf'],'Resolution',300)
        exportgraphics(f3,['SimulationOutput/',simID,'_ForecastLoad.pdf'],'Resolution',300)
        exportgraphics(f4,['SimulationOutput/',simID,'_ForecastRenewable.pdf'],'Resolution',300)
        exportgraphics(f5,['SimulationOutput/',simID,'_MeasuredW1.pdf'],'Resolution',300)
        exportgraphics(f6,['SimulationOutput/',simID,'_MeasuredW2.pdf'],'Resolution',300)
        exportgraphics(f7,['SimulationOutput/',simID,'_ForecastW1.pdf'],'Resolution',300)
        exportgraphics(f8,['SimulationOutput/',simID,'_ForecastW2.pdf'],'Resolution',300)

end

end
