function [Parameters, Load_Measure, Renewable_Measure, Load_Forecast, Renewable_Forecast, Load_Measure_Delta, Renewable_Measure_Delta, Load_Forecast_Delta, Renewable_Forecast_Delta, Pdisp_zero] = data_import_lower_res()    
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
    ControlSequenceDivision = 1;
    Parameters{29} = ControlSequenceDivision;

    % Compute the prediction horizon
    Np = 1;
    Parameters{8} = Np;

    % Number of steps each hour
    % IterationSegments = 1440;
    IterationSegments = 360;
    SegmentsInHour = 4;
    Parameters{16} = SegmentsInHour;
    Parameters{4} = IterationSegments;
    number_of_days = 5;
    Parameters{17} = number_of_days;

    % Hours of simulations 
    DataIntervals = number_of_days*24+1;
    SimulationSteps = DataIntervals*IterationSegments*SegmentsInHour;
    Parameters{3} = SimulationSteps;
    % Duration of the Simulation
    N = SimulationSteps;
    Parameters{9} = N;
    
    % SamplingTime
    SamplingTime = 2.5;       %[s]
    Parameters{2} = SamplingTime;
    
    % Constraints on the electrical machines states
    PowerAngleLimit = 30;
    Parameters{5} = PowerAngleLimit;
    FrequencyLimit = 0.04;
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
    
    Centroids = readmatrix("Input_Data/Centroids.csv");
    
    CentoidPositions = zeros(Na,2);
    for i = 1:Na
            CentoidPositions(i,1:2) = Centroids(CountryCodes(i),3:4);
    end
    Parameters{20} = CentoidPositions;


    %% Electrical topology data
    
    AdjacencyData = readmatrix("Input_Data/Adjacency_List.csv");
    
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
    CapacitiesData = readmatrix("Input_Data/Capacities.csv");
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
            dataread = readmatrix(['Input_Data/','0',num2str(CountryCodes(i)),'_Preprocessed.csv'])';
        else
            dataread = readmatrix(['Input_Data/',num2str(CountryCodes(i)),'_Preprocessed.csv'])';
        end
        
        % To consider data every 15 minutes
        w_forecast{i} = [dataread(1,:);dataread(3,:)]/1000;
        w_measured{i} = [dataread(2,:);dataread(4,:)]/1000;
        % To consider data every hour 
        % w_forecast{i} = [dataread(1,1:4:end);dataread(3,1:4:end)]/1000;
        % w_measured{i} = [dataread(2,1:4:end);dataread(4,1:4:end)]/1000;
        
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

    Load_Measure = zeros(Na,N+Np);
    Renewable_Measure = zeros(Na,N+Np);
    Load_Forecast = zeros(Na,N+Np);
    Renewable_Forecast = zeros(Na,N+Np);

    Load_Measure_Delta = zeros(Na,N+Np);
    Renewable_Measure_Delta = zeros(Na,N+Np);
    Load_Forecast_Delta = zeros(Na,N+Np);
    Renewable_Forecast_Delta = zeros(Na,N+Np);

    w_measured_inter = zeros(2*Na,N+Np);
    w_forecast_inter = zeros(2*Na,N+Np);
    Delta_w_measured_inter = zeros(2*Na,N+Np);
    Delta_w_forecast_inter = zeros(2*Na,N+Np);
    

    for h = 1:N+Np
        
        if h == DataIntervalsCounter 
            DataIntervalsCounter = DataIntervalsCounter + IterationSegments;
            DataIntCountIdx = DataIntCountIdx + 1;
        end
        k = 1;
        pos_idx = 1;
        for m = 1:Na
            if h == 1
                w_measured_inter(k:k+1,h) = [w_measured{m}(1,1);w_measured{m}(2,1)];
                Load_Measure(pos_idx,h) = w_measured_inter(k,h);
                Renewable_Measure(pos_idx,h) = w_measured_inter(k+1,h);

                w_forecast_inter(k:k+1,h) = [w_forecast{m}(1,1);w_forecast{m}(2,1)];
                Load_Forecast(pos_idx,h) = w_forecast_inter(k,h);
                Renewable_Forecast(pos_idx,h) = w_forecast_inter(k+1,h);

                Delta_w_measured_inter(k:k+1,h) = ((w_measured{m}(:,DataIntCountIdx+1)-w_measured{m}(:,DataIntCountIdx))/(IterationSegments))/SamplingTime;
                Load_Measure_Delta(pos_idx,h) = Delta_w_measured_inter(k,h);
                Renewable_Measure_Delta(pos_idx,h) = Delta_w_measured_inter(k+1,h);

                Delta_w_forecast_inter(k:k+1,h) = ((w_forecast{m}(:,DataIntCountIdx+1)-w_forecast{m}(:,DataIntCountIdx))/(IterationSegments))/SamplingTime;
                Load_Forecast_Delta(pos_idx,h) = Delta_w_forecast_inter(k,h);
                Renewable_Forecast_Delta(pos_idx,h) = Delta_w_forecast_inter(k+1,h);

                k = k + 2; 
                pos_idx = pos_idx + 1;
            else
                w_measured_inter(k:k+1,h) = w_measured_inter(k:k+1,h-1) + ((w_measured{m}(:,DataIntCountIdx+1)-w_measured{m}(:,DataIntCountIdx))/(IterationSegments)); 
                w_forecast_inter(k:k+1,h) = w_forecast_inter(k:k+1,h-1) + ((w_forecast{m}(:,DataIntCountIdx+1)-w_forecast{m}(:,DataIntCountIdx))/(IterationSegments)); 
                Delta_w_measured_inter(k:k+1,h) = ((w_measured{m}(:,DataIntCountIdx+1)-w_measured{m}(:,DataIntCountIdx))/(IterationSegments))/SamplingTime;
                Delta_w_forecast_inter(k:k+1,h) = ((w_forecast{m}(:,DataIntCountIdx+1)-w_forecast{m}(:,DataIntCountIdx))/(IterationSegments))/SamplingTime;

                Load_Measure(pos_idx,h) = w_measured_inter(k,h);
                Renewable_Measure(pos_idx,h) = w_measured_inter(k+1,h);

                  
                Load_Forecast(pos_idx,h) = w_forecast_inter(k,h);
                Renewable_Forecast(pos_idx,h) = w_forecast_inter(k+1,h);

                
                Load_Measure_Delta(pos_idx,h) = Delta_w_measured_inter(k,h);
                Renewable_Measure_Delta(pos_idx,h) = Delta_w_measured_inter(k+1,h);

                
                Load_Forecast_Delta(pos_idx,h) = Delta_w_forecast_inter(k,h);
                Renewable_Forecast_Delta(pos_idx,h) = Delta_w_forecast_inter(k+1,h);

                k = k + 2; 
                pos_idx = pos_idx + 1;
            end
        end
    end 






end
