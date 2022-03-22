from distributions import Distribution
from .client import Client

class CustomerAcquisition:

    def __init__(self, activeClients, lead_generation, conversion, churn) -> None:

        # Creating uncertainty distributions based on config file
        self.lead_generation = Distribution(**lead_generation)
        self.conversion = Distribution(**conversion)
        self.churn = Distribution(**churn)

        self.interested_clients = [0, 0, 0]
        self.active_clients = activeClients

    def step(self, actions):
        
        # actions_rel = actions["marketing"]

        # Convert interested clients
        conversion_rate = self.conversion.get_single()
        convert_dist = Distribution("bernoulli", {"p":conversion_rate})
        converted_clients = sum(convert_dist.rvs(size=self.interested_clients.pop()))
        self.active_clients.add_clients(converted_clients)

        # Create new interested clients and prepend them 
        self.interested_clients = [self.lead_generation.get_single()] + self.interested_clients


