from data_preprocessing import data_process_sampling


# ADD ARGPARSER
# Remember matrices Q and R in the argparser
# Add a sa parameter the list of electrical areas to simulate
# Add in argparser for dataset construction

# if __name__ == "__main__":




# %% Settings

# CONTRUCT DATASET

PLOT_DATA = True
STORE_DATA = True

control_time_step = 0.5 # seconds
number_hours = 24

data_process_sampling.preprocess_data(control_time_step, number_hours, PLOT_DATA, STORE_DATA)


# INITIALIZE NETWORK

# RUN MPC

# PLOT AND STORE RESULTS