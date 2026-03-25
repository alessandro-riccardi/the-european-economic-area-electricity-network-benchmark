import numpy as np

class LinearNetworkDynamics:

    def __init__(self, electrical_areas, network_topology):

        self.NUMBER_ATOMIC_AGENTS = len(electrical_areas)

        self.A = A
        self.B = B

    def step(self, x, u):
        return self.A @ x + self.B @ u