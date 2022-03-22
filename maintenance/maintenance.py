from queue import Queue

from expense import Expense
from shared.transport import Transport
from customerAquisition.client import Client
from germination.germinationStation import GerminationStation

class Maintenance:

    def __init__(self, maintenance_q: Queue, plant_store, maintenance_cost, transport: Transport, expense: Expense) -> None:
        self.maintenance_q = maintenance_q
        self.plant_store: GerminationStation = plant_store
        self.maintenance_cost = maintenance_cost
        self.transport = transport
        self.expense = expense

        self.client_list = []
        self.delayed_clients = []


    def step(self, action):

        while not self.maintenance_q.empty():
            client: Client = self.maintenance_q.get()["client"]
            self.manage_client(client)

        # Add back to q at the front
        for client in self.delayed_clients:
            self.maintenance_q.put({"client":client})

        self.transport.make_combined_jouney(self.client_list, plot_name=action["plot_maintenance"])
        
        self.client_list = []
        self.delayed_clients = []

    def manage_client(self, client: Client):
        if client.plant_varieties_requested is not None:
            plants = self.plant_store.get_plants(client.plant_varieties_requested)
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