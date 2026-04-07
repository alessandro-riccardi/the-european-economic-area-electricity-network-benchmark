# The European Economic Area Electricity Network Benchmark

Global README under writing. 

The EEA-ENB is undergoing a major update. New releases are happening in these weeks. If you need the previous version urgently, you can access it at the long term storage repository:  

> **Previous release** (stable): [https://doi.org/10.4121/d2c0d075-1c49-41af-8113-5e50c27ca97e](https://doi.org/10.4121/d2c0d075-1c49-41af-8113-5e50c27ca97e)

Old Readme


-- MATLAB version is for CMPC and DMPC-ADMM of the linear version of the benchmark. 

-- Python version is for CMPC and DMPC-ADMM of the linear and hybrid versions of the benchmark.

# The European Economic Area Electricity Network Benchmark (EEA-ENB)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A benchmark platform for the design, testing, and comparison of centralized and distributed Model Predictive Control (MPC) strategies applied to the European Economic Area electricity network. The benchmark models a multi-area power system with load, renewable generation, energy storage, dispatchable generation, and tie-line dynamics.

---

## Table of Contents

- [Overview](#overview)
- [What's New](#whats-new)
- [Repository Structure](#repository-structure)
- [System Model](#system-model)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Data Preprocessing](#data-preprocessing)
- [Control Strategies](#control-strategies)
- [Partitioning](#partitioning)
- [Output](#output)
- [Roadmap](#roadmap)
- [Notes on the MATLAB Version](#notes-on-the-matlab-version)

---

## Overview

The EEA-ENB provides a simulation environment for multi-area power system frequency and energy management control. Each area in the network is modeled as a dynamical system with five states and three control inputs, driven by measured and forecast load and renewable generation disturbances. The benchmark supports both centralized and distributed MPC formulations, solved via [Gurobi](https://www.gurobi.com/).

The network topology is derived from real EEA interconnections, and the electricity data (load and renewable generation) is sourced from real hourly measurements and forecasts, then resampled to arbitrary control time steps via cubic spline interpolation. This approach allows obtaining a sampled data-set for the simulations with any desired control time step, where the orginal data is availably at most every 15 minutes. 

Electricity and topological data for the EU is obtained from ENTSO-E's Transparency Platform ([https://transparency.entsoe.eu/](https://transparency.entsoe.eu/)). 

This new version of the benchmark also introduced UK as an additional area, which was not included in the previous version. Electricity data for UK is obtained from the Digest of UK Energy Statistics (DUKES) ([https://www.gov.uk/government/collections/digest-of-uk-energy-statistics-dukes](https://www.gov.uk/government/collections/digest-of-uk-energy-statistics-dukes)).

---

## What's New

### First Revision Highlights

- **Flexible data preprocessing**: Raw hourly electricity data is interpolated to any desired control time step using cubic splines. Both absolute power profiles and power increment (step) signals are generated for load and renewables, for all network areas.
- **Unified simulation entry point**: A new `main.py` orchestrates the full simulation pipeline — data preprocessing, topology construction, dynamics initialization, partitioning, reference generation, and closed-loop simulation — through a single argument-driven interface.
- **Centralized and Distributed MPC for linear dynamics**: Both `Centralized_MPC` and `Distributed_MPC` (via ADMM consensus) are fully implemented and selectable at runtime.
- **Configurable network partitioning**: Partition selection (centralized, distributed, or future algorithmic strategies) is handled modularly. PArtitioning strategies from other studies will be soon incorporated to further extend the repositoy.
- **Comprehensive documentation**: This README provides detailed explanations of the system model, data preprocessing steps, control strategies, and usage instructions to facilitate reproducibility and ease of use for researchers.

---

## Repository Structure

```
EEA-ENB/
│
├── main.py                          # Main simulation entry point
│
├── mpc_core/
│   ├── linear_network_dynamics.py   # Linear state-space model of the network
│   ├── mpc_centralized_linear.py    # Centralized MPC (CMPC) solver
│   ├── mpc_distributed_linear.py    # Distributed MPC via ADMM (DMPC-ADMM) solver
│   ├── network_dynamics.py          # Dynamic model constructor (linear/nonlinear dispatcher)
│   ├── optimization_matrices.py     # MPC prediction matrix builder (M, C, D, Q, R)
│   ├── reference_generator.py       # Reference trajectory generator
│   └── simulator.py                 # Simulation loop dispatcher
│
├── partitioning/
│   ├── partitioning_caller.py       # Network partitioning strategy selector
│   └── control_agents.py            # Augmented agent dynamics and cost matrix builder
│
├── data_preprocessing/
│   └── data_process_sampling.py     # Data resampling and spline interpolation pipeline
│
├── electricity_data/                # Preprocessed CSV datasets (generated by preprocessing)
│   ├── measured_load_dataset.csv
│   ├── forecast_load_dataset.csv
│   ├── measured_renewable_dataset.csv
│   ├── forecast_renewable_dataset.csv
│   ├── measured_load_increment_dataset.csv
│   ├── forecast_load_increment_dataset.csv
│   ├── measured_renewable_increment_dataset.csv
│   ├── forecast_renewable_increment_dataset.csv
│   ├── initial_dispatchable_power.csv
│   └── figures/                     # Auto-generated plots (PDF)
│
├── topological_data/
│   └── Network_Topology_Map.py      # EEA network topology and adjacency matrix builder
│
└── support_functions/
    ├── options.py                   # Argument parser (argparse)
    ├── data_loader.py               # Loads preprocessed electricity data from CSV
    ├── network_topology.py          # Extracts weighted adjacency matrix for selected areas
    ├── weighting_matrices.py        # Builds MPC cost matrices Q and R
    ├── network_bounds.py            # Computes state and input constraint bounds
    ├── inertia_modifiers.py         # Computes per-area inertia scaling factors
    ├── state_initializer.py         # Initializes the system state vector
    ├── empty_lists.py               # Utility: preallocates nested list structures
    └── data_plot.py                 # Plotting utilities
```

---

## Linear System Model

Each network area `i` is described by a **discrete-time linear state-space model**:

```
x_i(k+1) = A_i x_i(k) + B_i u_i(k) + D_i w_i(k)
```

### State vector (5 states per area)

| Index | Variable | Unit |
|-------|----------|------|
| 0 | Rotor angle deviation `δ` | deg |
| 1 | Frequency deviation `Δf` | Hz |
| 2 | Energy Storage System (ESS) energy | GW |
| 3 | Tie-line power flow | GW |
| 4 | Total dispatchable generated power | GW |

### Input vector (3 inputs per area — linear model)

| Index | Variable |
|-------|----------|
| 0 | Dispatchable power setpoint increment |
| 1 | ESS charging power |
| 2 | ESS discharging power |

### Disturbance vector (2 disturbances per area)

| Index | Variable |
|-------|----------|
| 0 | Load power increment |
| 1 | Renewable generation increment |

Inter-area coupling is encoded via the **weighted adjacency matrix** of the EEA network topology, affecting both the frequency deviation dynamics and the tie-line power flows. Inertia constants are area-dependent and scaled by the proportion of dispatchable generation capacity.

---

## Installation

### Requirements

- Python 3.8+
- [Gurobi](https://www.gurobi.com/) with a valid license (academic licenses available free of charge)

### Python dependencies

```bash
pip install numpy pandas scipy matplotlib gurobipy
```

---

## Usage

All simulations are launched from `main.py`. Parameters are set via command-line arguments directly in the `sys.argv` block (or via terminal):

```bash
python main.py \
  --control_time_step 0.25 \
  --number_hours 24 \
  --model linear \
  --control_strategy Distributed_MPC \
  --partitioning_strategy distributed \
  --simulation_horizon 100 \
  --prediction_horizon 10 \
  --reference_signal_generator Standard \
  --consensus_treshold 1e-6 \
  --plot_data True \
  --store_data True
```

To simulate a **subset of areas**, uncomment and set:

```bash
  --electrical_areas "[17, 2, 6, 10]"
```

### Simulation Pipeline

`main.py` executes the following steps in order:

1. Parse arguments
2. *(Optional)* Preprocess electricity data and compute topological data
3. Build the weighted adjacency matrix for the selected areas
4. Import preprocessed electricity datasets
5. Build MPC cost matrices `Q` and `R`, state/input bounds, and inertia modifiers
6. Construct the network dynamical model (`EEA_ENB`)
7. Partition the network into control agents
8. Build augmented agent dynamics and cost matrices
9. Compute the reference trajectory
10. Run the closed-loop MPC simulation
11. Plot results

---

## Configuration

| Argument | Type | Description |
|---|---|---|
| `--electrical_areas` | list | Areas to simulate (default: all). E.g. `[1, 2, 5]` |
| `--control_time_step` | float | Sampling period in seconds (e.g. `0.25`) |
| `--number_hours` | int | Length of the electricity data window in hours |
| `--model` | str | `linear` (nonlinear coming soon) |
| `--control_strategy` | str | `Centralized_MPC` or `Distributed_MPC` |
| `--partitioning_strategy` | str | `centralized`, `distributed` (others planned) |
| `--simulation_horizon` | int | Number of simulation time steps |
| `--prediction_horizon` | int | MPC prediction horizon length |
| `--reference_signal_generator` | str | Reference type (e.g. `Standard`) |
| `--state_weighting_matrix` | str | Custom `Q` matrix (default `[]` = identity-based) |
| `--input_weighting_matrix` | str | Custom `R` matrix (default `[]` = identity-based) |
| `--consensus_treshold` | float | ADMM convergence threshold (Distributed MPC) |
| `--preprocess_data` | flag | If set, reruns data preprocessing |
| `--plot_data` | bool | Plot results and data profiles |
| `--store_data` | bool | Save results and figures to disk |

---

## Data Preprocessing

Raw electricity data (load and renewable generation) is provided at native resolutions of 15, 30, or 60 minutes per area. The preprocessing pipeline in `data_preprocessing/data_process_sampling.py`:

1. Reads raw CSV files for each EEA area
2. Downsamples all signals to **hourly resolution**
3. Applies **cubic spline interpolation** (`scipy.interpolate.CubicSpline`) to resample to the target `control_time_step`
4. Computes **power increment signals** (`np.diff`) for both load and renewables
5. If measured and forecast signals are identical, adds **5% Gaussian noise** to introduce realistic variability
6. Converts all power values from **MW to GW**
7. Saves 8 CSV datasets and optionally PDF figures to `electricity_data/`

> Preprocessing only needs to be run once per `control_time_step`. Enable it by passing `--preprocess_data` on first use or when changing the sampling rate.

---

## Control Strategies

### Centralized MPC (`Centralized_MPC`)

A single Gurobi QP is solved at each time step over all network areas jointly. The full prediction matrices `M`, `C`, `D` are assembled for the entire network and the optimal input sequence is extracted for the first step (receding horizon).

### Distributed MPC via ADMM (`Distributed_MPC`)

Each control agent solves a **local Gurobi QP** over its augmented neighbourhood (own area + direct neighbours). Consensus on shared variables is enforced iteratively via the **Alternating Direction Method of Multipliers (ADMM)**:

- Local optimization per agent
- Average variable computation across copies
- Dual variable (`γ`) update
- Convergence checked via primal and dual residual norms

ADMM terminates when residual norms for all agents fall below `epsilon_convergence`, or after `max_number_of_iterations`.

Both strategies enforce:
- Input bounds (dispatchable power ramp, ESS charge/discharge limits)
- State bounds (angle deviation, frequency deviation, ESS energy, total generation)

---

## Partitioning

Network partitioning is managed in `partitioning/partitioning_caller.py`:

| Strategy | Description |
|---|---|
| `centralized` | Single agent controls all areas |
| `distributed` | One agent per area; each augmented with its direct network neighbours |
| `algorithmic` | *(Planned)* Graph-based automatic partitioning |
| `genetic_algorithm` | *(Planned)* Evolutionary partitioning optimisation |
| `load_partitioning` | *(Planned)* Load a custom partition from file |

The `compute_control_agents_matrices` function in `partitioning/control_agents.py` builds the local `A`, `B`, `D`, `Q`, `R` matrices for each augmented agent by selecting the relevant rows/columns from the global system matrices.

---

## Output

After simulation, the following variables are returned and plotted:

| Variable | Shape | Description |
|---|---|---|
| `x_evolution` | `(NUM_STATES × N_areas, T+1)` | State trajectory |
| `u_evolution` | `(NUM_INPUTS × N_areas, T+1)` | Input trajectory |
| `w_evolution` | `(2 × N_areas, T+1)` | Disturbance trajectory |
| `residual_evolution` | `(max_iterations,)` | ADMM residual per iteration (Distributed only) |
| `Core_Seconds` | nested list | Per-agent, per-iteration solve times |
| `Simulation_Total_Time` | float | Total wall-clock time in seconds |

Plots generated (per area):
- Rotor angle deviation
- Frequency deviation
- ESS energy
- Tie-line power
- Total generated power
- External disturbances `w1` (load) and `w2` (renewables)

---

## Roadmap

- [ ] **Nonlinear hybrid dynamical systems model** with hybrid MPC control (in progress)
- [ ] **Algorithmic and genetic algorithm partitioning** strategies
- [ ] **MPC controller based on hybrid dynamical model and Mixzed-Integer Programming**
- [ ] Argument parser extension: custom `Q`/`R` matrices, area list from CLI
- [ ] Results storage to structured output files

---

## Notes on the MATLAB Version

A MATLAB implementation of the benchmark (CMPC and DMPC-ADMM, linear dynamics) is available in the legacy MATLAB folder. **The MATLAB version will not be updated further.** All future development will be carried out in Python.

---

## Citation

If you use this benchmark in your research, please cite the original release:

```
@incollection{riccardi2025benchmark,
  title={A benchmark for the application of distributed control techniques to the electricity network of the European economic area},
  author={Riccardi, Alessandro and Laurenti, Luca and De Schutter, Bart},
  booktitle={Control systems benchmarks},
  pages={9--28},
  year={2025},
  publisher={Springer}
}
```
