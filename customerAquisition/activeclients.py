from .client import Client
from distributions import Distribution

class ActiveClients:

    def __init__(self, distributions, plant_requester, plant_request_length, 
                 revenue, expense, cac, client_details) -> None:
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
        self.client_details = client_details
        self.revenue = revenue
        self.expense = expense
        self.cac = cac

        self.churned = 0


    def step(self, actions):
        # Could log which clients are getting removed / what theyre all doing
        # Prune active clients
        if actions["customer_change"] is not None:
            details = actions["customer_change"]
            self.churn_base = details["churn"]
            self.cac["values"] = details["cac"]
            self.unit_distribution_dist = Distribution(**details["unit"])

        client_mask = []
        for client in self.clients:
            if client.step_subscription() == "cancelled":
                client_mask.append(False)
            else:
                client_mask.append(True)

        self.churned = len(client_mask) - sum(client_mask)
        self.clients = [client for client, mask in zip(self.clients, client_mask) if mask]


    def add_clients(self, client_count):

        # Add acquisition cost for customers
        cac = self.select_cac(client_count)
        self.expense.make_payment(
            name="Customer Acquisition",
            tag="customer_acquisition",
            amount=cac*client_count,
        )

        for i in range(client_count):
            unitCount = int(self.unit_distribution_dist.get_single())
            subLength = int(self.subLength_dist.get_single())
            officePosition = self.office_position_dist.get_array(size=2)

            self.clients.append(Client(
                unitCount, subLength, officePosition, self.churn_base, self.plant_base, 
                self.plant_request_length, self.plant_requester, self.revenue, self.client_details
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
        return self.cac["values"][-1]

    @property
    def active_units(self):
        return sum([x.unit_count for x in self.clients])

    @property
    def subscription_price(self):
        return self.client_details["subscription_price"]
    @property
    def purchase_price(self):
        return self.client_details["purchase_price"]