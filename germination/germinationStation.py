from itertools import chain
from random import sample
from unicodedata import name
import numpy as np

from ..expense import Expense

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

        self.plant_store = [[0 for __ in range(self.weeks_2_maturity + self.mature_life)] for _ in GerminationStation.plant_varieties]
        self.plant_requests = [0 for _ in GerminationStation.plant_varieties]
        

    def step(self, actions):

        # Remove dead plants
        for store in self.plant_store:
            store.pop(0)

        if sum(self.plant_requests) == 0:
            for variety, store in enumerate(self.plant_store):
                if variety < self.active_varieties:
                    store.append(self.extra_production)

        elif sum(self.plant_requests) + self.total_plants <= self.total_plant_space:
            for store, request in zip(self.plant_store, self.plant_requests):
                store.append(request)

            # Add buffer plants
            if sum(self.plant_requests) + self.total_plants + self.active_varieties*self.extra_production <= self.total_plant_space:
                for variety, store in enumerate(self.plant_store):
                    if variety < self.active_varieties:
                        store.append(self.extra_production)
            self.plant_requests = [0 for _ in GerminationStation.plant_varieties]
        else:
            # Randomly sample from requests to fill space
            spaces = self.total_plant_space - self.total_plants
            request_expanded = list(chain(*[[i]*count for i, count in enumerate(self.plant_requests)]))

            sampled = sample(request_expanded, spaces)
            sampled_grouped = [sampled.count(i) for i, _ in enumerate(GerminationStation.plant_varieties)]
            for variety, count in enumerate(sampled_grouped):
                self.plant_store[variety].append(count)
                self.plant_requests[variety] -= count

        # Expense all the costs
        total_seeds_planted = sum([x[-1] for x in self.plant_store])
        self.expense.make_payment(
            name="seed_planting",
            tag="germination",
            amount=total_seeds_planted*self.cost_per_seed
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



    def make_request(self, plants):
        plants = list(plants)
        plant_counts = [plants.count(i) for i, _ in enumerate(GerminationStation.plant_varieties)]
        self.plant_requests = [a + b for a, b in zip(self.plant_requests, plant_counts)]

    def get_plants(self, request):
        request_grouped = [request.count(i) for i, _ in enumerate(GerminationStation.plant_varieties)]
        difference = [a - b for a, b in zip(self.mature_plants, request_grouped)]
        # Can provide all requested plants
        if all([x >= 0 for x in difference]):
            self._remove_plants(request_grouped)
            return request
        else:
            return None

    def _remove_plants(self, request_grouped):
        for variety, count in enumerate(request_grouped):
            for i in range(self.mature_life):
                if count > self.plant_store[variety][i]:
                    count -= self.plant_store[variety][i]
                    self.plant_store[variety][i] = 0
                else:
                    self.plant_store[variety][i] -= count
                    count = 0
                    break

    @property 
    def total_plant_space(self):
        return self.shelf_count*self.seeds_per_shelf

    @property
    def total_plants(self):
        return sum(chain(*self.plant_store))

    @property
    def mature_plants(self):
        return [sum(x[:self.mature_life]) for x in self.plant_store]