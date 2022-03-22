from queue import Queue
from customerAquisition.client import Client
from shared.transport import Transport
from expense import Expense


class InstallUnits:

    def __init__(self, transport: Transport, install_q: Queue[list[Client]], install_cost, expense: Expense, plant_store) -> None:
        self.transport = transport
        self.install_q = install_q
        self.install_cost = install_cost
        self.delayed_installs = []

        self.expense = expense
        self.plant_store = plant_store

    def step(self, actions):
        installs: list[Client] = self.delayed_installs + self.install_q.get()
        self.delayed_installs = []

        for client in installs:
            fuel_cost = self.transport.make_single_journey(client.office_position)
            plants = self.plant_store.get_plants(client.plant_varieties_requested)
            
            if plants is not None:
                client.installed = True
                self.expense.make_payment(
                    name=f"Client{client.id}-Install",
                    tag="build",
                    amount=fuel_cost + self.install_cost,
                )
                client.receive_plants(plants)
            else:
                self.delayed_installs.append(client)

            
