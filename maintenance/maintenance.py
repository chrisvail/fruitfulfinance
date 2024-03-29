from queue import Queue
from time import perf_counter

from expense import Expense
from shared.transport import Transport
from customerAquisition.client import Client
from germination.germinationStation import GerminationStation

class Maintenance:

    # timing = {
    #     "manage":{"time":0, "count":0},
    #     "transport":{"time":0, "count":0},
    #     "queueDelayed":{"time":0, "count":0},
    #     "getPlants":{"time":0, "count":0},
    #     "delayedClients":{"time":0, "count":260},
    #     "actualClients":{"time":0, "count":260},
    # }

    def __init__(self, maintenance_q: Queue, plant_store, maintenance_cost, transport: Transport, expense: Expense) -> None:
        self.maintenance_q = maintenance_q
        self.plant_store: GerminationStation = plant_store
        self.maintenance_cost = maintenance_cost
        self.transport = transport
        self.expense = expense

        self.client_list = []
        self.delayed_clients = []


    def step(self, action):

        # t0 = perf_counter()
        while not self.maintenance_q.empty():
            client: Client = self.maintenance_q.get()["client"]
            self.manage_client(client)
        # Maintenance.timing["manage"]["time"] += perf_counter() - t0
        # Maintenance.timing["manage"]["count"] += 1
        
        # Add back to q at the front
        # t0 = perf_counter()
        for client in self.delayed_clients:
            self.maintenance_q.put({"client":client})
        # Maintenance.timing["queueDelayed"]["time"] += perf_counter() - t0
        # Maintenance.timing["queueDelayed"]["count"] += 1

        # t0 = perf_counter()
        transport_cost = self.transport.make_combined_jouney(self.client_list, plot_name=action["plot_maintenance"])
        self.expense.make_payment(
            name="Transport",
            tag="maintenance",
            amount = transport_cost
        )
        # Maintenance.timing["transport"]["time"] += perf_counter() - t0
        # Maintenance.timing["transport"]["count"] += 1
        
        # Maintenance.timing["delayedClients"]["time"] += len(self.delayed_clients)
        # Maintenance.timing["actualClients"]["time"] += len(self.client_list)
        self.client_list = []
        self.delayed_clients = []

    def manage_client(self, client: Client):
        if client.plant_varieties_requested is not None:
            # t0 = perf_counter()
            plants = self.plant_store.get_plants(client.plant_varieties_requested)
            # Maintenance.timing["getPlants"]["time"] += perf_counter() - t0
            # Maintenance.timing["getPlants"]["count"] += 1
            if plants is not None:
                self.client_list.append(client)
                self.expense.make_payment(
                    name=f"Client{client.id}",
                    tag="maintenance",
                    amount=client.unit_count*self.maintenance_cost
                )
            else: 
                self.delayed_clients.append(client)
        else:
            self.client_list.append(client)
            self.expense.make_payment(
                    name=f"Client{client.id}",
                    tag="maintenance",
                    amount=client.unit_count*self.maintenance_cost
                )

    # def __del__(self):
    #     print("\nMaintenance")
    #     for k, v in Maintenance.timing.items():
    #         print(f"\t{k}\t{v['time']}\t{v['count']}\t{v['time']/max([v['count'], 1])}")