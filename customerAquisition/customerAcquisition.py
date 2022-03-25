from distributions import Distribution
from .client import Client
import numpy as np

class CustomerAcquisition:

    def __init__(self, activeClients, lead_generation, conversion, lead_growth) -> None:

        # Creating uncertainty distributions based on config file
        self.lead_generation = Distribution(**lead_generation)
        self.conversion = Distribution(**conversion)
        self.lead_growth = lead_growth

        self.interested_clients = [0, 0, 0]
        self.active_clients = activeClients

    def step(self, actions):
        
        # actions_rel = actions["marketing"]

        if actions["customer_change"] is not None:
            details = actions["customer_change"]
            steps = details["steps"]
            self.lead_growth = details["lead_growth"]
            new_mean = details["lead_growth"]**steps
            new_lead_gen = details["lead_generation"]

            if new_lead_gen["name"] == "constant":
                new_lead_gen["parameters"]["value"] = new_mean
            elif new_lead_gen["name"] == "poisson":
                new_lead_gen["parameters"]["mu"] = new_mean
            else:
                new_lead_gen["parameters"]["loc"] = new_mean
            self.lead_generation = Distribution(**new_lead_gen)



        if self.interested_clients[0] > 0:
            converted_clients = np.sum(self.conversion.get_array(size=int(self.interested_clients.pop(0))))
            self.active_clients.add_clients(converted_clients)
        else:
            self.interested_clients.pop(0)

        # Create new interested clients and prepend them 
        self.interested_clients.append(int(self.lead_generation.get_single()))

    
        if self.lead_generation.name == "constant":
            params = self.lead_generation.parameters
            params["value"] *= self.lead_growth
        elif self.lead_generation.name == "poisson":
            params = self.lead_generation.parameters
            params["mu"] *= self.lead_growth
        else:
            params = self.lead_generation.parameters
            params["loc"] *= self.lead_growth
        self.lead_generation.update_param(params)
        # print(f"\tInterested Client: {self.interested_clients}")


