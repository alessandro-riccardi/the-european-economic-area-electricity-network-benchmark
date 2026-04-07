import numpy as np
import matplotlib.pyplot as plt

ALPHA   = 2
ETA_MIN = 0.05
ETA_MAX = 0.95

def eta_exp(e, e_max, alpha=ALPHA, exchange_mode='charging'):
    s = e / e_max
    if exchange_mode == 'charging':
        return ETA_MIN + (ETA_MAX - ETA_MIN) * (np.exp(-alpha * (1 - s)) - 1) / (np.exp(-alpha) - 1)
    elif exchange_mode == 'discharging':
        return ETA_MIN + (ETA_MAX - ETA_MIN) * (np.exp(alpha * (1 - s)) - 1) / (np.exp(alpha) - 1)

# --- Test rate behaviour ---
e_max = 100.0
e_vec = np.linspace(0, e_max, 500)

plt.plot(e_vec, eta_exp(e_vec, e_max, exchange_mode='charging'),    label='eta_c (charging)')
plt.plot(e_vec, eta_exp(e_vec, e_max, exchange_mode='discharging'), label='eta_d (discharging)')
plt.xlabel('SoC [%]')
plt.ylabel('rate')
plt.legend()
plt.grid(True)
plt.show()


# Test batterey behaviour

x_0 = 0
u_charge = 1
u_discharge = -0.2

x_evolution = np.zeros(500)
x_evolution[0] = x_0

for time_step in range(1,250):
    x_plus = x_evolution[time_step-1] + u_charge * eta_exp(x_evolution[time_step-1], e_max, exchange_mode='charging')
    
    if x_plus < e_max:
        x_evolution[time_step] = x_plus 
    else:
        x_evolution[time_step] = e_max

for time_step in range(250,500):
    x_plus = x_evolution[time_step-1] + u_discharge / eta_exp(x_evolution[time_step-1], e_max, exchange_mode='discharging')
    
    if x_plus > 0:
        x_evolution[time_step] = x_plus 
    else:
        x_evolution[time_step] = 0

# Plot results

plt.plot(x_evolution, label='SoC evolution')
plt.xlabel('Time step')
plt.ylabel('SoC [%]')
plt.grid(True)
plt.show()