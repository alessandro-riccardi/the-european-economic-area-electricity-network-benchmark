# European Economic Area Electricity Network

## Introduction 

The European Economic Area Electricity Network Benchmark (EEA-ENB) is a multi-area power system representing the European network of transmission systems for electricity to facilitate the application of distributed control techniques. In the EEA-ENB we consider the Load Frequency Control (LFC) problem in the presence of renewable energy sources (RESs), and energy storage systems (ESSs). RESs are known to cause instability in power networks due to their inertia-less and intermittent characteristics, while ESSs are introduced as a resource to mitigate the problem. In the EEA-ENB, particular attention is dedicated to Distributed Model Predictive Control (DMPC), whose application is often limited to small and homogeneous test cases due to the lack of standardized large-scale scenarios for testing, and due to the large computation time required to obtain a centralized MPC action for performance comparison with DMPC strategies under consideration. The second problem is exacerbated when the scale of the system grows. To address these challenges and to provide a real-world-based and control-independent benchmark, the EEA-ENB has been developed. The benchmark includes a centralized MPC strategy providing performance and computation time metrics to compare distributed control within a repeatable and realistic simulation environment.

## MATLAB Code Documentation

This GitLab documentation describes a MATLAB simulation code for an energy system. The code performs a Model Predictive Control (MPC) operation for managing power generation and distribution in a network of areas. The code includes data import, optimization, and results visualization. The MATLAB code is organized as follows:

- [ ] main.m: this is the principal script to run the control simulation.  
- [ ] data_import.m: this script reads the preprocessed data about load demands and renewable generation measurements and forecasts stored in .csv files, and returns the parameters and signals required for the simulation.
- [ ] opt_matrices.m: this script is used to build the matrices used by the optimizaer to obtain the control action. Thier construction is performed according to the formulation of the optimization problem reported in the book chapter.
- [ ] GurobiCaller.m: this script is used to run the Gurobi optimizaer
- [ ] state_update_model.m and state_update_plant.m: which are identical files in this first formulation, but might be distinguished later to implement model mismatches or parameters inaccuracies. The former is used to simulate the system dynamics, and the latter as a prediction model for the centralized MPC strategy.  
- [ ] plot_results.m:  used to produce plots of the simulation results and input data.

In the following, further details are provided for each individual scipt. This will help understanding the meaning of variables and parameters, and the role of each function. To improve the overall documentation, each script is divided in sections, and the role of each section is reported below.

### main.m

   1. **Initialization**
      - Clear variables, clear command window, and close all figures.
      - Set format for numerical notation.
      - Define the simulation ID.

   2. **Simulation Options**
      - Define options for plotting and exporting input/output data.

   3. **Simulation Parameters and Data Import**
      - Import data and parameters from data_import.m.
      - Extract relevant parameters for the simulation.

   4. **Solver Parameters**
      - Set convergence tolerance for the optimization solver.

   5. **Vectors Preallocation**
      - Preallocate arrays for storing states, inputs, optimization results, and time vectors. 

   6. **Optimization Matrices**
      - Calculate matrices used in the optimization problem using opt_matrices.m.

   7. **Initial Conditions**
      - Set initial conditions for the state and input variables.

   8. **MPC**
      - Implement the MPC control loop over a predefined number of iterations.
      - Update disturbance forecasts and perform optimization.
      - Update state, input, and store optimization results.

   9. **Results Export**
      - Optionally export the simulation results from the workspace.

   10. **Plots**
      - Optionally plot and visualize the simulation results.

   **Usage**: To run the code, follow these steps:
      - 1. Ensure that MATLAB and Gurobi are installed on your system. The code was tested with Matlab r2023b and Gurobi 10.03
      - 2. Copy the code to a MATLAB script or function file.
      - 3. Adjust the simulation options, parameters, and initial conditions as needed.
      - 4. Run the script in MATLAB.

   **Note**: The simulation of 24 hours of operation was performed using a processor Intel Xeon E5-2637v3, with a base clock of 3.5 GHz, and cumpled with 128 GB of RAM. it requiered 206 hours, 15 minutes, and 24 seconds to be completed. 


### data_import.m

This script is designed to handle various aspects of data import, processing, and visualization for the EEA-ENB. It is a crucial part of the simulation workflow and ensures that data is correctly imported and preprocessed for further analysis. It includes various sections for setting up parameters, importing data, interpolating data, and optionally plotting and exporting input data.

   1. **Simulation Parameters**

      This section sets up the simulation parameters:

      - **Parameters**: A cell array used to store simulation parameters.
      - **CountryCodes**: A list of country codes used in the simulation.
      - **Na**: Number of electrical areas.
      - **ControlSequenceDivision**: A vector defining the control sequence structure for blocking.
      - **Np**: The prediction horizon in steps.
      - **IterationSegments**: The number of steps per hour.
      - **DataIntervals**: The number of hours of simulation.
      - **SamplingTime**: Sampling time in seconds.
      - **PowerAngleLimit** and **FrequencyLimit**: Constraints on electrical machine states.

   2. **Electrical Areas Parameters**

      This section defines parameters related to electrical areas:

      - **Kp**: Gain of electrical machines.
      - **Tp**: Time constant of electrical machines.
      - **nc** and **nd**: Charging and discharging rates of energy storage systems (ESSs).
      - **BatteryPowerScaling** and **BatteryCapacityScaling**: Parameters used for ESS constraints.

   3. **Optimization Parameters**

      This part sets up matrices for optimization:

      - **Ac**, **Bc**, and **Ec**: Optimization matrices.
      - **KPtie**: A parameter for extending the cost function.

   4. **Country ISO Labels**

      This section handles country codes and labels:

      - **CISO**: Country ISO codes.
      - **CISO_Import**: A list of selected country labels for import.
      - **Centroids** and **CentoidPositions**: Geographical coordinates.

   5. **Electrical Topology Data**

      This part deals with electrical topology data:

      - **AdjacencyData** and **A**: Import and creation of the adjacency matrix.
      - **AW**: Weighting matrix.
      - **DAvg** and **KLine**: Average distance and a scaling parameter.

   6. **Dispatchable Sources and Battery Capacities Limits**

      Here, data on dispatchable sources and battery capacities are imported and processed:

      - **CapacitiesData**: Import of capacities data.
      - **AreaLimits**: Lower and upper bounds on capacities.
      - **LowerBound** and **UpperBound**: Control bounds for the simulation.

   7. **Data Import**

      Data on electrical load and renewable generation is imported and processed:

      - **w_forecast** and **w_measured**: Preallocated cell arrays for data.
      - **w_measured_inter**, **Delta_w_measured_inter**, **Delta_w_forecast_inter**, and **w_forecast_inter**: Interpolated data.
      - **Pdisp_zero** and **w_zero**: Initial conditions.

   8. **Input Data Plot**

      This section is for optional plotting of input data. Several figures are generated for visualizing the data.

   9. **Export Graphic**

      This section allows for exporting the generated figures as image files if `export_input_plot` is set to true.


### opt_matrices.m

This script is used to contruct the optimization matrices used to solve quadratic programm as defined in the book chapter. The matrices are designed such that state contraints are expressed as input functions.

   1. **Simulation Parameters**
      This section is used to retrieve the necessary parameters for the construction of the optimization matrices

   2. **Preallocation**
      Initializes matrices and ensures they are the correct dimensions.

   3. **Computation of the Optimization Matrices**
      Computes the matrices. Some theoretical understanding of the topic is requiered to understand the construction process. For that we referr to [REF].


### GurobiCaller.m

This script builds the Gurobi model for the quadratic programming problem and calls the optimizer. For further details referr to the Gurobi documentation [REF].

### state_update_model.m and state_update_plant.m

Those functions perform the state update considering the dynamic equations input power, and disturbances for multiple electrical areas. The power exchange between different areas is also considered, and the updated state is provided as output. They are equal in this firt formulation, but they can be characterize represent model mismatches and uncertainties.

   1. **Parameters**

      The following parameters are used in the state update model:
      - `DT`: Time step (seconds).
      - `Na`: Number of electrical areas.
      - `Kp`: Gain of electrical machines.
      - `Tp`: Time constant of electrical machines.
      - `nc`: Charging rate of energy storage systems (ESSs).
      - `nd`: Discharging rate of ESSs.
      - `A`: Interaction matrix for areas.
      - `AW`: Weighting matrix for areas interaction.
      - `KLine`: Scaling parameter for line interactions.

   2. **Vectors Preallocation**

      Several vectors are preallocated to store intermediate results and final values:
      - `x_plus`: Updated state vector for all areas.
      - `Pedge`: Power exchanged between areas.
      - `PedgeTotal`: Total power exchanged for each area.
      - `Pdisp`: Dispatchable power for each area.
      - `PESS_c`: Charging power for each ESS.
      - `PESS_d`: Discharging power for each ESS.
      - `Pren`: Renewable power disturbance for each area.
      - `Pload`: Load power disturbance for each area.

   3. **Vectors Redefinition**

      In this section, input and disturbance variables are redifined to enhance readbility of the code.

   4. **Areas Interactions**

      This section calculates power exchanges (`Pedge`) between different areas based on the area interaction matrix (`A`) and the weighting matrix (`AW`). It also computes the total power exchanged (`PedgeTotal`) for each area.

   5. **State Dynamics Equations**

      For each area, the state dynamics equations are applied to update the state variables based on the state vector (`x_h`), inputs (`u_h`), and disturbances (`w_h`). The state variables are updated using the state transition matrix `Ai`, input matrix `Bi`, and disturbance matrix `Wi`, defined for each area `i`.

      - `x_j`: State vector for the current area.
      - `u_j`: Input vector for the current area.
      - `w_j`: Disturbance vector for the current area.

      The updated state vector `x_plus` is constructed, and the loop continues for all areas.


### plot_results.m

This function is used to visualize and plot the results of a simulation. It generates multiple figures showing different aspects of the simulation, including power angle deviation, frequency deviation, energy storage, dispatchable generation, load curves, renewable generation, tie lines transmission, and cost functions.

   1. **Parameters**
      - `simID`: A unique identifier for the simulation.
      - `export_output_plot`: A boolean value to determine whether to export the generated plots.
      - `x`: Simulation data for state variables.
      - `u`: Simulation data for control inputs.
      - `w`: Simulation data for disturbances.
      - `PedgeTieLine`: Simulation data for tie line power variations.
      - `JVect`: Simulation data for cost functions.
      - `Parameters`: A cell array containing various simulation parameters.
