from itertools import chain
from random import sample
from unicodedata import name
import numpy as np

from expense import Expense

class GerminationStation:

    plant_varieties = [
        "Rocket",
        "Strawberries",
        "Basil",
        "Thyme",
        "Tomatoes",
        "Mint",
        "Romaine Lettuce",
        "Habenero Peppers",
        "Rosemary",
        "Cress",
        "Sweet Peppers"
        "Oregano"
    ]

    details = {
        "Mature Plants":0,
        "Mature Plants2":0,
        "Total Plants":0,
        "Plants Requested":0,
        "Plants Requested2":0,
        "Plants Requested3":0,
        "Plants Requested4":0,
        "Plants Lost":0,
        "Full":0,
        "Failed Gets":0,
        "Free Space":0
    }

    def __init__(self, germination_costs, plant_maturity, initial_shelf_counts, active_varieties, expense: Expense) -> None:
        self.expense = expense

        self.cost_per_seed = germination_costs["cost_per_seed"]
        self.seeds_per_shelf = germination_costs["seeds_per_shelf"]
        self.new_shelf_capex = germination_costs["new_shelf_capex"]
        self.shelf_running_cost = germination_costs["shelf_running_cost"]
        self.new_shelving_unit_capex = germination_costs["new_shelving_unit_capex"]
        self.shelves_per_shelving_unit = germination_costs["shelves_per_shelving_unit"]
        self.extra_production = germination_costs["extra_production"]
        self.active_varieties = active_varieties

        self.weeks_2_maturity = plant_maturity["weeks2mature"]
        self.mature_life = plant_maturity["mature_life"]

        self.shelf_unit_count = initial_shelf_counts[0]
        self.shelf_count = initial_shelf_counts[1]

        self.expense.make_payment(
            name="shelving_units_capex",
            tag="germination",
            amount=self.shelf_unit_count*self.new_shelving_unit_capex
        )

        self.expense.make_payment(
            name="shelf_capex",
            tag="germination",
            amount=self.shelf_count*self.new_shelf_capex
        )

        self.plant_store = np.zeros((self.mature_life + self.weeks_2_maturity, len(GerminationStation.plant_varieties)))
        self.plant_requests = np.zeros(len(GerminationStation.plant_varieties))
        # self.plant_requests = [0 for _ in GerminationStation.plant_varieties]
    

    def step(self, actions):

        # Remove dead plants
        
        GerminationStation.details["Plants Lost"] += np.sum(self.plant_store[0])/260
        self.plant_store = self.plant_store[1:]

        GerminationStation.details["Plants Requested2"] += sum(self.plant_requests)/260
        GerminationStation.details["Mature Plants"] += sum(self.mature_plants)/260

        if self.spaces_available == 0:
            new_plants = np.zeros(len(GerminationStation.plant_varieties))
        # if no space, sample from requests to make full
        elif np.sum(self.plant_requests) > self.spaces_available:
            sample = np.random.choice(
                len(GerminationStation.plant_varieties),
                size=self.spaces_available,
                replace=True,
                p=self.plant_requests/np.sum(self.plant_requests)
            )

            new_plants = self.bucket_plants(sample)
            self.plant_requests -= new_plants
        # Fill extra production with sample if no space
        elif int(np.sum(self.plant_requests)*self.extra_production) > self.spaces_available:
            sample = np.random.choice(
                len(GerminationStation.plant_varieties),
                size=self.spaces_available - np.sum(self.plant_requests),
                replace=True,
                p=self.plant_requests/np.sum(self.plant_requests)
            )

            new_plants = self.bucket_plants(sample)
            new_plants += self.plant_requests
            self.plant_requests = np.zeros(len(GerminationStation.plant_varieties))
        else:
            GerminationStation.details["Free Space"] += 1
            new_plants = np.ceil(self.plant_requests*self.extra_production).astype(np.int32)
            GerminationStation.details["Plants Requested3"] += np.sum(new_plants)/260
            self.plant_requests = np.zeros(len(GerminationStation.plant_varieties))


        new_plants = np.reshape(new_plants, (1, len(GerminationStation.plant_varieties)))
        self.plant_store = np.append(self.plant_store, new_plants, axis=0)

        

        # Expense all the costs
        
        self.expense.make_payment(
            name="seed_planting",
            tag="germination",
            amount=np.sum(new_plants)*self.cost_per_seed
        )

        total_shelves = np.ceil(self.total_plants/self.seeds_per_shelf)
        self.expense.make_payment(
            name="shelf_operation",
            tag="germination",
            amount=total_shelves*self.shelf_running_cost
        )

        new_shelves = actions["add_new_shelves"]
        if new_shelves != 0:
            self.shelf_count += new_shelves
            new_shelving_units = np.ceil(self.shelf_count / self.shelves_per_shelving_unit)
            if new_shelving_units > self.shelf_unit_count:
                self.expense.make_payment(
                    name="shelving_units_capex",
                    tag="germination",
                    amount=(new_shelving_units-self.shelf_unit_count)*self.new_shelving_unit_capex
                )
            self.expense.make_payment(
                name="shelf_capex",
                tag="germination",
                amount=new_shelves*self.new_shelf_capex
            )
        


        GerminationStation.details["Total Plants"] += self.total_plants/260
        GerminationStation.details["Mature Plants2"] += self.mature_plants/260
        if self.total_plants == self.total_plant_space: GerminationStation.details["Full"] += 1
        GerminationStation.details["Plants Requested4"] += new_plants/260


    def make_request(self, plants):
        GerminationStation.details["Plants Requested"] += len(plants)/260

        plant_counts = self.bucket_plants(plants)
        self.plant_requests += plant_counts

    def get_plants(self, request):
        request_grouped = self.bucket_plants(request)
        difference = self.mature_plants - request_grouped

        # Cant provide plants
        if np.any(difference < 0):
            GerminationStation.details["Failed Gets"] += 1
            return None
        else:
            self._remove_plants(request_grouped)
            return request
        

    def _remove_plants(self, request):
        for i, plants in enumerate(self.plant_store[:self.mature_life, :]):
            for j, x in enumerate(plants):
                diff = x - request[j]

                if diff >= 0:
                    self.plant_store[i, j] = diff
                    request[j] = 0
                else:
                    self.plant_store[i, j] = 0
                    request[j] = -diff

    @property 
    def total_plant_space(self):
        return self.shelf_count*self.seeds_per_shelf

    @property
    def total_plants(self):
        return np.sum(self.plant_store, axis=None)

    @property
    def mature_plants(self):
        return np.sum(self.plant_store[:self.mature_life, :], axis=0)

    @property
    def spaces_available(self):
        return self.total_plant_space - self.total_plants

    def bucket_plants(self, plants: np.ndarray):
        return np.array([np.sum(np.where(plants == i, 1, 0)) for i, _ in enumerate(GerminationStation.plant_varieties)])

    def __del__(self):
        print("\nGermination Station")
        for k, v in GerminationStation.details.items():
            print(f"\t{k}\t{v}")