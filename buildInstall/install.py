from queue import Queue
from ..customerAquisition.client import Client
from ..shared.transport import Transport
from ..expense import Expense


class InstallUnits:

    def __init__(self, transport: Transport, install_q: Queue[list[Client]], install_cost, expense: Expense) -> None:
        self.transport = transport
        self.install_q = install_q
        self.install_cost = install_cost

        self.expense = expense

    def step(self, actions):
        installs = self.install_q.get()

        for client in installs:
            client.installed = True
            fuel_cost = self.transport.make_single_journey(client.office_position)
            self.expense.make_payment(
                name=f"Client{client.id}-Install",
                tag="build",
                amount=fuel_cost + self.install_cost,
            )
