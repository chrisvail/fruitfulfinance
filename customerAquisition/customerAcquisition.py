from distributions import Distribution
from .client import Client
import numpy as np

class CustomerAcquisition:

    def __init__(self, activeClients, lead_generation, conversion) -> None:

        # Creating uncertainty distributions based on config file
        self.lead_generation = Distribution(**lead_generation)
        self.conversion = Distribution(**conversion)

        self.interested_clients = [0, 0, 0]
        self.active_clients = activeClients

    def step(self, actions):
        
        # actions_rel = actions["marketing"]

        if self.interested_clients[0]:
            
            converted_clients = np.sum(self.conversion.get_array(size=int(self.interested_clients.pop(0))))
            self.active_clients.add_clients(converted_clients)
        else:
            self.interested_clients.pop(0)

        # Create new interested clients and prepend them 
        self.interested_clients.append(int(self.lead_generation.get_single()))
        print(f"\tInterested Client: {self.interested_clients}")


