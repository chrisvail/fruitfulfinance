import numpy as np

from ..customerAquisition.client import Client

class Transport:
    
    def __init__(self, hq_position, fuel_cost, max_clients_serviced) -> None:
        self.hq_position = hq_position
        self.fuel_cost = fuel_cost
        self.max_clients_serviced = max_clients_serviced
        

    
    def make_single_journey(self, location):
        # Assume manhattan distances
        distance_travelled = np.sum(np.abs(self.hq_position - location))
        return 2*distance_travelled*self.fuel_cost

    def make_combined_jouney(self, clients: list[Client]):
        # Make multiple journeys

        client_count = len(clients)
        chunked_clients = [clients[i:i + self.max_clients_serviced] for i in range(0, client_count, self.max_clients_serviced)]
        total_distance = 0
        for chunk in chunked_clients:

            visited = [self.hq_position]
            unvisited = chunk[:]
            curr_position = self.hq_position

            while unvisited:
                next_client = [np.inf]
                for client in unvisited:
                    dist = np.sum(np.abs(curr_position - client.office_position))
                    if dist < next_client[0]:
                        next_client = [dist, client]
                
                total_distance += next_client[0]
                curr_position = next_client[1]
                visited.append(next_client[1])
                unvisited.remove(next_client[1])

            visited.append(self.hq_position)
            total_distance += np.sum(np.abs(curr_position - self.hq_position))

        return total_distance*self.fuel_cost