import numpy as np
from matplotlib import pyplot as plt
from scipy import rand

from customerAquisition.client import Client
from distributions import Distribution

class Transport:
    
    def __init__(self, hq_position, fuel_cost, max_clients_serviced) -> None:
        self.hq_position = Distribution(**hq_position).get_array(size=2)
        self.fuel_cost = fuel_cost
        self.max_clients_serviced = max_clients_serviced
        

    
    def make_single_journey(self, location):
        # Assume manhattan distances
        distance_travelled = np.sum(np.abs(self.hq_position - location))
        return 2*distance_travelled*self.fuel_cost

    # def make_combined_jouney(self, clients: list[Client], plot_name=None):
    #     # Make multiple journeys

    #     if plot_name is not None:
    #         fig, ax = plt.subplots(1,1)
    #         ax.scatter(x=self.hq_position[0], y=self.hq_position[1], s=10, c="r")

    #     client_count = len(clients)
    #     chunked_clients = [clients[i:i + self.max_clients_serviced] for i in range(0, client_count, self.max_clients_serviced)]
    #     total_distance = 0
    #     for chunk in chunked_clients:
    #         client_locations = np.array([x.office_position for x in chunk])

    #         hq = self.hq_position.reshape((1, 2))
    #         visited = np.concatenate((hq, client_locations, hq), axis=0)
    #         total_distance = np.sum(np.abs(np.diff(visited, 1, axis=0)), axis=None)

    #         if plot_name is not None:
    #             ax.scatter(
    #                 x=client_locations[:,0], y=client_locations[:,1], 
    #                 s=[client.unit_count for client in chunk],
    #                 c=[np.random.rand(1)[0]]*len(client_locations),
    #                 alpha=0.5
    #             )
    #             visited = np.reshape(np.concatenate(visited, axis=0), (len(chunk)+2, 2))
    #             ax.plot(visited[:,0], visited[:,1])
        
    #     if plot_name is not None:
    #         plt.savefig(f"{plot_name}.png")

    #     return total_distance*self.fuel_cost





    def make_combined_jouney(self, clients: list[Client], plot_name=None):
        # Make multiple journeys

        if plot_name is not None:
            fig, ax = plt.subplots(1,1)
            ax.scatter(x=self.hq_position[0], y=self.hq_position[1], s=10, c="r")

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
                curr_position = next_client[1].office_position
                visited.append(next_client[1].office_position)
                unvisited.remove(next_client[1])

            visited.append(self.hq_position)
            total_distance += np.sum(np.abs(curr_position - self.hq_position))
            client_locations = np.array([x.office_position for x in chunk])

            if plot_name is not None:

                ax.scatter(
                    x=client_locations[:,0], y=client_locations[:,1], 
                    s=[client.unit_count for client in chunk],
                    c=[np.random.rand(1)[0]]*len(client_locations),
                    alpha=0.5
                )
                visited = np.reshape(np.concatenate(visited, axis=0), (len(chunk)+2, 2))
                ax.plot(visited[:,0], visited[:,1])
        
        if plot_name is not None:
            plt.savefig(f"{plot_name}.png")

        return total_distance*self.fuel_cost