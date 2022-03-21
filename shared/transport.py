

import numpy as np


class Transport:
    
    def __init__(self, hq_position, fuel_cost, max_journey_length, max_units_maintained) -> None:
        self.hq_position = hq_position
        self.fuel_cost = fuel_cost
        self.max_jouney_length = max_journey_length
        self.max_units_maintained = max_units_maintained

    
    def make_single_journey(self, location):
        # Assume manhattan distances
        distance_travelled = np.sum(np.abs(self.hq_position - location))
        return distance_travelled*self.fuel_cost

    def make_combined_jouney(self, locations):
        # Make multiple journeys
        pass