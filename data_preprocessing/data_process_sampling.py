# %% Import libraries
import numpy as np
import pandas as pd
import os
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt


def preprocess_data(control_time_step, number_hours, PLOT_DATA, STORE_DATA):
    """
    Preprocess electricity load and renewable generation data for multiple areas.

    Reads raw CSV data for each area, resamples it to a uniform hourly resolution,
    interpolates it to a finer time grid using cubic splines, and computes
    power increment (step) signals. Optionally plots and saves the results.

    Parameters
    ----------
    control_time_step : float
        Desired time resolution of the output datasets in seconds (e.g., 0.5).
    PLOT_DATA : bool
        If True, generates and displays plots of load and renewable profiles
        (absolute values and increments) for each area.
    STORE_DATA : bool
        If True, saves the interpolated datasets and figures to CSV and PDF files
        in the parent directory under 'electricity_data/'.

    Returns
    -------
    None
        Results are stored to disk when STORE_DATA is True. The following CSV files
        are written to '../electricity_data/':
            - measured_load_dataset.csv
            - forecast_load_dataset.csv
            - measured_renewable_dataset.csv
            - forecast_renewable_dataset.csv
            - measured_load_increment_dataset.csv
            - forecast_load_increment_dataset.csv
            - measured_renewable_increment_dataset.csv
            - forecast_renewable_increment_dataset.csv

    Notes
    -----
    - Input CSVs must reside in the same directory as this script.
    - Load and renewable data may have 15-, 30-, or 60-minute native resolution;
      the function downsamples all to hourly before interpolation.
    - If measured and forecast signals are identical, Gaussian noise (5% of the
      signal range) is added to the measured signal to introduce variability.
    - Power values are converted from MW to GW (divided by 1000).
    """

    # %% Settings
    # Set plotting parameters
    # plt.rcParams.update({
    #     "text.usetex": True,
    #     "font.family": "serif",
    #     "font.serif": ["Times New Roman"],
    #     "font.size": 14
    # })


    # %% Import data
    current_folder = os.path.dirname(os.path.abspath(__file__))
    data_file_time_steps = os.path.join(current_folder, 'time_steps.csv')
    data_frame_time_steps  = pd.read_csv(data_file_time_steps, sep=",")
    time_steps = data_frame_time_steps.iloc[:,2:].to_numpy()

    number_areas = time_steps.shape[0]

    # Check this if correspondsa

    t_data = np.arange(number_hours+1)

    t_original = np.arange(number_hours+1) * 60 * 60 # 1h = 3600 seconds

    # New time axis: one point every control_time_step
    t_interpolation = np.arange(0, t_original[-1] + control_time_step, control_time_step)
        

    # %% Preallocate datasets

    measured_load_dataset = np.zeros((len(t_interpolation), number_areas))
    forecast_load_dataset = np.zeros((len(t_interpolation), number_areas))
    measured_renewable_dataset = np.zeros((len(t_interpolation), number_areas))
    forecast_renewable_dataset = np.zeros((len(t_interpolation), number_areas))

    measured_load_increment_dataset = np.zeros((len(t_interpolation)-1, number_areas))
    forecast_load_increment_dataset = np.zeros((len(t_interpolation)-1, number_areas))
    measured_renewable_increment_dataset = np.zeros((len(t_interpolation)-1, number_areas))
    forecast_renewable_increment_dataset = np.zeros((len(t_interpolation)-1, number_areas))


    # %% Process data

    for area_idx in range(number_areas):
        if area_idx < 9:
            data_file_load = os.path.join(current_folder, f'0{area_idx+1}_Load.csv')
            data_file_renewable = os.path.join(current_folder, f'0{area_idx+1}_Renewable.csv')
        else:
            data_file_load = os.path.join(current_folder, f'{area_idx+1}_Load.csv')
            data_file_renewable = os.path.join(current_folder, f'{area_idx+1}_Renewable.csv')

        area = data_frame_time_steps.iloc[area_idx]['Area']
        data_frame_load = pd.read_csv(data_file_load, sep=",")
        data_frame_renewable = pd.read_csv(data_file_renewable, sep=",")
        
        # Convert n/e and N/A to 0
        data_frame_renewable = data_frame_renewable.replace('n/e', 0)
        data_frame_renewable = data_frame_renewable.replace('N/A', 0)

        if time_steps[area_idx,0] == 15:
            time_duration = 4*(number_hours+1)
            forecast_total_load = (data_frame_load.iloc[:time_duration:4,1].to_numpy())/1000
            actual_total_load = (data_frame_load.iloc[:time_duration:4,2].to_numpy())/1000
        elif time_steps[area_idx,0] == 30:
            time_duration = 2*(number_hours+1)
            forecast_total_load = (data_frame_load.iloc[:time_duration:2,1].to_numpy())/1000
            actual_total_load = (data_frame_load.iloc[:time_duration:2,2].to_numpy())/1000
        else:
            time_duration = number_hours+1
            forecast_total_load = (data_frame_load.iloc[:time_duration:1,1].to_numpy())/1000
            actual_total_load = (data_frame_load.iloc[:time_duration:1,2].to_numpy())/1000
        
        if time_steps[area_idx,1] == 15:
            time_duration = 4*(number_hours+1)
            forecast_total_renewable = (data_frame_renewable.iloc[:time_duration:4,2].to_numpy() + \
                                    data_frame_renewable.iloc[:time_duration:4,5].to_numpy() + \
                                    data_frame_renewable.iloc[:time_duration:4,8].to_numpy())/1000
            actual_total_renewable = (data_frame_renewable.iloc[:time_duration:4,3].to_numpy() + \
                                    data_frame_renewable.iloc[:time_duration:4,6].to_numpy() + \
                                    data_frame_renewable.iloc[:time_duration:4,9].to_numpy())/1000
        elif time_steps[area_idx,1] == 30:
            time_duration = 2*(number_hours+1)
            forecast_total_renewable = (data_frame_renewable.iloc[:time_duration:2,2].to_numpy() + \
                                    data_frame_renewable.iloc[:time_duration:2,5].to_numpy() + \
                                    data_frame_renewable.iloc[:time_duration:2,8].to_numpy())/1000
            actual_total_renewable = (data_frame_renewable.iloc[:time_duration:2,3].to_numpy() + \
                                    data_frame_renewable.iloc[:time_duration:2,6].to_numpy() + \
                                    data_frame_renewable.iloc[:time_duration:2,9].to_numpy())/1000
        else:
            time_duration = number_hours+1
            forecast_total_renewable = (data_frame_renewable.iloc[:time_duration:1,2].to_numpy() + \
                                    data_frame_renewable.iloc[:time_duration:1,5].to_numpy() + \
                                    data_frame_renewable.iloc[:time_duration:1,8].to_numpy())/1000
            actual_total_renewable = (data_frame_renewable.iloc[:time_duration:1,3].to_numpy() + \
                                    data_frame_renewable.iloc[:time_duration:1,6].to_numpy() + \
                                    data_frame_renewable.iloc[:time_duration:1,9].to_numpy())/1000

        

        # Add variability to equal signals
        if np.sum(actual_total_load) == np.sum(forecast_total_load):
            
            signal_magnitude = np.max(actual_total_load) - np.min(actual_total_load)
            noise_std = 0.05 * signal_magnitude

            noise = np.random.normal(0, noise_std, size=actual_total_load.shape)
            actual_total_load = actual_total_load + noise
            # print("Added noise to load signals in area ", area_idx+1)

        # Fit cubic spline and evaluate at new time points
        cs = CubicSpline(t_original, forecast_total_load)
        forecast_total_load_interp = cs(t_interpolation)
        cs = CubicSpline(t_original, actual_total_load)
        actual_total_load_interp = cs(t_interpolation)

        
        # Add variability to equal signals
        if np.sum(actual_total_renewable) == np.sum(forecast_total_renewable):
            
            signal_magnitude = np.max(actual_total_renewable) - np.min(actual_total_renewable)
            noise_std = 0.05 * signal_magnitude

            noise = np.random.normal(0, noise_std, size=actual_total_renewable.shape)
            actual_total_renewable = actual_total_renewable + noise
            # print("Added noise to renewable signals in area ", area_idx+1)


        cs = CubicSpline(t_original, forecast_total_renewable)
        forecast_total_renewable_interp = cs(t_interpolation)
        cs = CubicSpline(t_original, actual_total_renewable)
        actual_total_renewable_interp = cs(t_interpolation)

        # Compute variation steps
        forecast_total_load_step = np.diff(forecast_total_load_interp)
        actual_total_load_step = np.diff(actual_total_load_interp)
        forecast_total_renewable_step = np.diff(forecast_total_renewable_interp)
        actual_total_renewable_step = np.diff(actual_total_renewable_interp)

        # Construct datasets
        measured_load_dataset[:, area_idx] = actual_total_load_interp
        forecast_load_dataset[:, area_idx] = forecast_total_load_interp
        measured_renewable_dataset[:, area_idx] = actual_total_renewable_interp
        forecast_renewable_dataset[:, area_idx] = forecast_total_renewable_interp

        measured_load_increment_dataset[:, area_idx] = actual_total_load_step
        forecast_load_increment_dataset[:, area_idx] = forecast_total_load_step
        measured_renewable_increment_dataset[:, area_idx] = actual_total_renewable_step
        forecast_renewable_increment_dataset[:, area_idx] = forecast_total_renewable_step




        if PLOT_DATA:

            fig_1, ax_1 = plt.subplots(figsize=(7, 4.5))
            # plt.step(t_data, actual_total_load,where='post', label='Load measurement')
            # plt.step(t_data, forecast_total_load,where='post', linestyle='--', label='Load forecast')
            # plt.step(t_original, actual_total_load, where='post', color = 'blue', label='Load measurement')
            # plt.step(t_original, forecast_total_load, where='post', color = 'green', linestyle='--', label='Load forecast')
            plt.step(t_interpolation, actual_total_load_interp, where='post', color = 'blue', label= "Load measurement")
            plt.step(t_interpolation, forecast_total_load_interp, where='post', color = 'green', linestyle='--', label= "Load forecast")
            ax_1.set_ylabel('Power [GW]')
            ax_1.set_xlabel(f'Time [s]')
            ax_1.set_title(f'Load area {area_idx+1} - {area}')
            ax_1.legend()
            ax_1.grid(True, linestyle='--', color='lightgrey')
            ax_1.set_xticks(np.arange(0, t_interpolation[-1]+1, 3*t_interpolation[-1]/number_hours))
            ax_1.set_xlim(t_interpolation[0], t_interpolation[-1])
            plt.tight_layout()
            plt.show()

            fig_2, ax_2 = plt.subplots(figsize=(7, 4.5))
            # plt.step(t_original, actual_total_renewable, where='post', color = 'blue', label='Renewable measurement')
            # plt.step(t_original, forecast_total_renewable, where='post', color = 'green', linestyle='--', label='Renewable forecast')
            plt.step(t_interpolation, actual_total_renewable_interp, where='post', color = 'blue', label= "Renewable measurement")
            plt.step(t_interpolation, forecast_total_renewable_interp, where='post', color = 'green', linestyle='--', label= "Renewable forecast")
            ax_2.set_ylabel('Power [GW]')
            ax_2.set_xlabel(f'Time [s]')
            ax_2.set_title(f'Renewable area {area_idx+1} - {area}')
            ax_2.legend()
            ax_2.grid(True, linestyle='--', color='lightgrey')
            ax_2.set_xticks(np.arange(0, t_interpolation[-1]+1, 3*t_interpolation[-1]/number_hours))
            ax_2.set_xlim(t_interpolation[0], t_interpolation[-1])
            # plt.xlim(t_interpolation[0], t_interpolation[-1])
            plt.tight_layout()
            plt.show()

            fig_3, ax_3 = plt.subplots(figsize=(7, 4.5))
            plt.step(t_interpolation[0:-1], actual_total_load_step, where='post', color = 'blue', label= "Actual Load Increments")
            plt.step(t_interpolation[0:-1], forecast_total_load_step, where='post', color = 'green', linestyle='--', label= "Forecast Load Increments")
            ax_3.set_ylabel('Power [GW]')
            ax_3.set_xlabel(f'Time [s]')
            ax_3.set_title(f'Load power step area {area_idx+1} - {area}')
            ax_3.legend()
            ax_3.grid(True, linestyle='--', color='lightgrey')
            ax_3.set_xticks(np.arange(0, t_interpolation[-1]+1, 3*t_interpolation[-1]/number_hours))
            ax_3.set_xlim(t_interpolation[0], t_interpolation[-1])
            # plt.xlim(t_interpolation[0], t_interpolation[-1])
            plt.tight_layout()
            plt.show()

            fig_4, ax_4 = plt.subplots(figsize=(7, 4.5))
            plt.step(t_interpolation[0:-1], actual_total_renewable_step, where='post', color = 'blue', label= "Actual Renewable Increments")
            plt.step(t_interpolation[0:-1], forecast_total_renewable_step, where='post', color = 'green', linestyle='--', label= "Forecast Renewable Increments")
            ax_4.set_ylabel('Power [GW]')
            ax_4.set_xlabel(f'Time [s]')
            ax_4.set_title(f'Renewable power step area {area_idx+1} - {area}')
            ax_4.legend()
            ax_4.grid(True, linestyle='--', color='lightgrey')
            ax_4.set_xticks(np.arange(0, t_interpolation[-1]+1, 3*t_interpolation[-1]/number_hours))
            ax_4.set_xlim(t_interpolation[0], t_interpolation[-1])
            # plt.xlim(t_interpolation[0], t_interpolation[-1])
            plt.tight_layout()
            plt.show()

            if STORE_DATA:
                file_path = os.path.normpath(os.path.join(current_folder, '..', 'electricity_data/figures', f'area_{area_idx+1}_load_plot.pdf'))
                fig_1.savefig(file_path, dpi = 300, bbox_inches="tight")   
                file_path = os.path.normpath(os.path.join(current_folder, '..', 'electricity_data/figures', f'area_{area_idx+1}_renewable_plot.pdf'))
                fig_2.savefig(file_path, dpi = 300, bbox_inches="tight")
                file_path = os.path.normpath(os.path.join(current_folder, '..', 'electricity_data/figures', f'area_{area_idx+1}_load_increments_plot.pdf'))
                fig_3.savefig(file_path, dpi = 300, bbox_inches="tight")
                file_path = os.path.normpath(os.path.join(current_folder, '..', 'electricity_data/figures', f'area_{area_idx+1}_renewable_increments_plot.pdf'))
                fig_4.savefig(file_path, dpi = 300, bbox_inches="tight")




    # %% Store results

    if STORE_DATA:
        target_path = os.path.normpath(os.path.join(current_folder, '..', 'electricity_data', 'measured_load_dataset.csv'))
        np.savetxt(target_path, measured_load_dataset, delimiter=",", fmt='%g')
        target_path = os.path.normpath(os.path.join(current_folder, '..', 'electricity_data', 'forecast_load_dataset.csv'))
        np.savetxt(target_path, forecast_load_dataset, delimiter=",", fmt='%g')
        target_path = os.path.normpath(os.path.join(current_folder, '..', 'electricity_data', 'measured_renewable_dataset.csv'))
        np.savetxt(target_path, measured_renewable_dataset, delimiter=",", fmt='%g')
        target_path = os.path.normpath(os.path.join(current_folder, '..', 'electricity_data', 'forecast_renewable_dataset.csv'))
        np.savetxt(target_path, forecast_renewable_dataset, delimiter=",", fmt='%g')

        target_path = os.path.normpath(os.path.join(current_folder, '..', 'electricity_data', 'measured_load_increment_dataset.csv'))
        np.savetxt(target_path, measured_load_increment_dataset, delimiter=",", fmt='%g')
        target_path = os.path.normpath(os.path.join(current_folder, '..', 'electricity_data', 'forecast_load_increment_dataset.csv'))
        np.savetxt(target_path, forecast_load_increment_dataset, delimiter=",", fmt='%g')
        target_path = os.path.normpath(os.path.join(current_folder, '..', 'electricity_data', 'measured_renewable_increment_dataset.csv'))
        np.savetxt(target_path, measured_renewable_increment_dataset, delimiter=",", fmt='%g')
        target_path = os.path.normpath(os.path.join(current_folder, '..', 'electricity_data', 'forecast_renewable_increment_dataset.csv'))
        np.savetxt(target_path, forecast_renewable_increment_dataset, delimiter=",", fmt='%g')


