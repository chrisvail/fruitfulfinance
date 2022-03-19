from ..distributions import Distribution
from .client import Client

class CustomerAcquisition:

    def __init__(self, organic, advertising, events, conversion, churn) -> None:

        # Creating uncertainty distributions based on config file
        self.organic = Distribution(**organic)
        self.advertising = Distribution(**advertising)
        self.events = Distribution(**events)
        self.conversion = Distribution(**conversion)
        self.churn = Distribution(**churn)

        self.interested_clients = [0, 0, 0]
        self.active_clients = []

    def step(self, actions):
        
        # actions_rel = actions["marketing"]

        # Prune active clients
        client_mask = []
        for client in self.active_clients:
            if client.step_subscription() == "cancelled":
                client_mask.append(False)
            else:
                client_mask.append(True)

        self.active_clients = [client for client, mask in zip(self.active_clients, client_mask) if mask]

        # Convert interested clients
        conversion_rate = self.conversion.get_single()
        convert_dist = Distribution("bernoulli", {"p":conversion_rate})
        converted_clients = sum(convert_dist.rvs(size=self.interested_clients.pop()))
        for i in range(converted_clients):
            self.active_clients.append(Client)

        # Create new interested clients and prepend them 
        self.interested_clients = [sum([
            self.organic.get_single(),
            self.advertising.get_single(),
            self.events.get_single()
        ])] + self.interested_clients


