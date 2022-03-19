from .client import Client
from ..distributions import Distribution

class ActiveClients:

    def __init__(self, distributions, plant_requester, revenue, plant_request_length) -> None:
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


    def add_clients(self, client_count):

        for i in range(client_count):

            unitCount = int(self.unit_distribution_dist.get_single())
            subLength = int(self.subLength_dist.get_single())
            officePosition = self.office_position_dist.get_array(size=2)

            self.clients.append(Client(
                unitCount, subLength, officePosition, self.churn_base, self.plant_base, 
                self.plant_request_length, self.plant_requester, self.revenue
            ))