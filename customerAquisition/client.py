from ..distributions import Distribution
from ..misc_functions import get_subscription_cost, get_plant_count, get_unit_cost

class Client:

    client_count = 0
    client_churned = 0
    expected_request_delay = 4
    churn_addition = 0.025
    churn_subtraction = 0.001
    churn_min = 0.05

    def __init__(self, unitCount, subLength, officePosition, churn, plant_dist, plant_request_length, plant_requests, revenue) -> None:
        self.unit_count = unitCount
        self.office_position = officePosition

        self.revenue.make_payment(
                    name=f"Client{self.id}",
                    reason="sale",
                    amount=get_unit_cost(self.unit_count)
                )

        self.sub_length = subLength
        self.client_lifetime = 0

        self.churn = Distribution(**churn)
        self.plant_dist = Distribution(**plant_dist)
        self.plant_request_length = plant_request_length
        self.plant_request = plant_requests
        self.plant_request.make_request(self.plant_dist.get_array(get_plant_count(self.unit_count)))
        self.plants_requested = None
        

        self.id = Client.client_count
        Client.client_count += 1

        self.subscription_cost = get_subscription_cost(self.unit_count)
        self.revenue = revenue

    
    def step_subscription(self):
        self.client_lifetime += 1
        if self.client_lifetime % self.plant_request_length == 0:
            self.plant_request.make_request(self.plant_dist.get_array(get_plant_count(self.unit_count)))
            self.plants_requested = self.client_lifetime
        
        if self.plants_requested is not None \
           and (self.client_lifetime - self.plants_requested) > Client.expected_request_delay:

           if self.churn.name == "binomial":
                p = self.churn.parameters["p"]
                p += Client.churn_addition
        else:
            if self.churn.name == "binomial":
                p = self.churn.parameters["p"]
                p -= Client.churn_min
                if p < Client.churn_min: p = Client.churn_min

        if self.client_lifetime % self.sub_length == 0:
            if self.churn.get_single():
                return "cancelled"
            else:
                self.revenue.make_payment(
                    name=f"Client{self.id}",
                    reason="subscription",
                    amount=self.subscription_cost
                )
                return "continued"

    def receive_plants(self, plants):
        # Ignore plants - not important
        self.plants_requested = None
        
        
