clear all
clc
close all

% Figures in light theme
s = settings;
s.matlab.appearance.figure.GraphicsTheme.TemporaryValue = "light";

% For notation
format shortE 

% Simulation Name
simID = 'Input_Data\';
Output_Data = 'Output_Data\';
simIDDynamics = 'Dynamics\';

%% Options

plot_input_data = true;
visibility_option = 'off';
export_data_plot = true;
print_labels = false;

export_data = true;


%% Data import

[Parameters, Load_Measure, Renewable_Measure, Load_Forecast, Renewable_Forecast,...
 Load_Measure_Delta, Renewable_Measure_Delta, Load_Forecast_Delta, Renewable_Forecast_Delta, Pdisp_zero] = data_import();


%% Plot data

if plot_input_data == true
    plot_data(Parameters, Load_Measure, Renewable_Measure, Load_Forecast, Renewable_Forecast,...
              Load_Measure_Delta, Renewable_Measure_Delta, Load_Forecast_Delta, Renewable_Forecast_Delta,...
              export_data_plot, print_labels, Output_Data, visibility_option)
end


%% Matrices of the dynamics

[A, B, D, Area_Matrices] = system_dynamics(Parameters);


%% Export processed data

Na = Parameters{7};

if export_data == true
    writematrix(Load_Measure, [Output_Data,'0A_MeasuredLoad.csv'])
    writematrix(Renewable_Measure, [Output_Data,'0B_MeasuredRenewable.csv'])
    writematrix(Load_Forecast,[Output_Data,'0C_ForecastLoad.csv'])
    writematrix(Renewable_Forecast, [Output_Data,'0D_ForecastRenewable.csv'])
    writematrix(Load_Measure_Delta,[Output_Data,'0E_MeasuredLoadIncrements.csv'])
    writematrix(Renewable_Measure_Delta,[Output_Data,'0F_MeasuredRenewableIncrements.csv'])
    writematrix(Load_Forecast_Delta,[Output_Data,'0G_ForecastLoadIncrements.csv'])
    writematrix(Renewable_Forecast_Delta,[Output_Data,'0H_ForecastRenewableIncrements.csv'])
    writematrix(Pdisp_zero,[Output_Data,'0I_DispatchablePower_zero.csv'])
    for i = 1:Na
        if i < 10
            ID_name = ['0',num2str(i)];
        else
            ID_name = num2str(i);
        end
        writematrix(Area_Matrices{i}{1},[simIDDynamics,'A_',ID_name,'.csv'])
        writematrix(Area_Matrices{i}{2},[simIDDynamics,'B_',ID_name,'.csv'])
        writematrix(Area_Matrices{i}{3},[simIDDynamics,'D_',ID_name,'.csv'])
    end
end