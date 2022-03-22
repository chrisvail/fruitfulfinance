from distributions import Distribution

class Client:

    client_count = 0
    client_churned = 0
    expected_request_delay = 4
    churn_addition = 0.025
    churn_subtraction = 0.001
    churn_min = 0.05

    def __init__(self, unitCount, subLength, officePosition, churn, plant_dist, plant_request_length, germination_request, revenue, client_details) -> None:
        self.unit_count = unitCount
        self.office_position = officePosition


        self.sub_length = subLength
        self.client_lifetime = 0

        self.churn = Distribution(**churn)
        self.plant_dist = Distribution(**plant_dist)
        self.plant_request_length = plant_request_length
        self.germination_request = germination_request
        self.plant_varieties_requested = self.plant_dist.get_array(size=self.plants_per_unit*self.unit_count)
        self.germination_request.make_request(self.plant_varieties_requested)
        self.plants_requested = None

        self.purchase_price = client_details["purchase_price"]
        self.subscription_price = client_details["subscription_price"]
        self.plants_per_unit = client_details["plants_per_unit"]

        self.revenue.make_payment(
                    name=f"Client{self.id}",
                    tag="sale",
                    amount=self.purchase_price*self.unit_count,
                    details={
                        "units":unitCount,
                        "client":self,
                    }
                )

        self.installed = False
        

        self.id = Client.client_count
        Client.client_count += 1

        self.revenue = revenue

    
    def step_subscription(self):

        if not self.installed: return "uninstalled"

        self.client_lifetime += 1
        if self.client_lifetime % self.plant_request_length == 0:
            self.plant_varieties_requested = self.plant_dist.get_array(size=self.plants_per_unit*self.unit_count)
            self.germination_request.make_request(self.plant_varieties_requested)
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
                    tag="subscription",
                    amount=self.subscription_price*self.unit_count,
                    details={
                        "client":self
                    }
                )
                return "continued"
        return "in contract"

    def receive_plants(self, plants):
        # Ignore plants - not important
        self.plants_requested = None
        self.plant_varieties_requested = None
        
        
