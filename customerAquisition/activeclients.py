from .client import Client
from ..distributions import Distribution

class ActiveClients:

    def __init__(self, distributions, plant_requester, plant_request_length, revenue, expense, cac) -> None:
        self.clients = []

        # Creation of clients
        #   > Creation distributions
        #       - Unit count
        #       - subLength
        #       - office position
        #       - plant requests
        #  
        #   > Continuing distributions
        #       - Churn
        #       - plant dist
        #  
        # Sending objects
        #   > Revenue
        #   > Plant Requester 

        
        self.unit_distribution_dist = Distribution(**distributions["unit"])
        self.subLength_dist = Distribution(**distributions["subLength"])
        self.office_position_dist = Distribution(**distributions["officePosition"])

        self.churn_base = distributions["churn"]
        self.plant_base = distributions["plantDist"]

        self.plant_requester = plant_requester 
        self.plant_request_length = plant_request_length
        self.revenue = revenue
        self.expense = expense
        self.cac = cac


    def step(self, actions):
        # Could log which clients are getting removed / what theyre all doing
        # Prune active clients
        client_mask = []
        for client in self.clients:
            if client.step_subscription() == "cancelled":
                client_mask.append(False)
            else:
                client_mask.append(True)

        self.clients = [client for client, mask in zip(self.active_clients, client_mask) if mask]


    def add_clients(self, client_count):

        # Add acquisition cost for customers
        cac = self.select_cac(client_count)
        self.expense.make_payment(
            name="Customer Acquisition",
            tag="Customer Acquisition",
            amount=cac*client_count,
        )

        for i in range(client_count):
            unitCount = int(self.unit_distribution_dist.get_single())
            subLength = int(self.subLength_dist.get_single())
            officePosition = self.office_position_dist.get_array(size=2)

            self.clients.append(Client(
                unitCount, subLength, officePosition, self.churn_base, self.plant_base, 
                self.plant_request_length, self.plant_requester, self.revenue
            ))

    def select_cac(self, customers):
        # Threshold
        # Value

        # self.cac = {
        #   "thresholds":[5, 10, 25],
        #   "values":[210, 120, 90]
        # }

        for i, threshold in enumerate(self.cac["thresholds"]):
            if customers > threshold:
                continue
            else:
                return self.cac["values"][i]