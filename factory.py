from queue import Queue

from buildInstall.build import BuildUnit
from buildInstall.install import InstallUnits
from customerAquisition.activeclients import ActiveClients
from customerAquisition.customerAcquisition import CustomerAcquisition
from germination.germinationStation import GerminationStation
from maintenance.maintenance import Maintenance
from shared.transport import Transport
from expense import Expense
from revenue import Revenue
from distributions import Distribution



class Simulation:

    def __init__(self, clock, config) -> None:
        # Create queues for passing information
        build_q = Queue()
        install_q = Queue()
        maintenance_q = Queue()

        # Build cashflow capture
        self.expense = Expense()
        self.revenue = Revenue(build_q, maintenance_q)

        # Create transportation
        transport = Transport(**config["transport"])

        # Create germination station
        germination_station = GerminationStation(
            expense=self.expense, 
            **config["germinationStation"]
        )


        # Customer Acquisition System
        # Create simulation cac values
        cac_low = Distribution(**config["cac"]["cac_low"]).get_single()
        cac_med = Distribution(**config["cac"]["cac_med"]).get_single()
        cac_high = Distribution(**config["cac"]["cac_high"]).get_single()
        config["activeClients"]["cac"]["values"] = [cac_low, cac_med, cac_high]

        active_clients = ActiveClients(
            revenue=self.revenue, 
            expense=self.expense, 
            plant_requester=germination_station,
            **config["activeClients"]
        )

        customer_acquisition = CustomerAcquisition(
            activeClients=active_clients,
            **config["customerAcquisition"]
        )

        # Build system
        build = BuildUnit(
            expense=self.expense,
            build_q=build_q,
            install_q=install_q,
            **config["build"]
        )

        install = InstallUnits(
            transport=transport,
            install_q=install_q,
            expense=self.expense,
            plant_store=germination_station,
            **config["install"]
        )

        # Maintenance
        maintenance = Maintenance(
            maintenance_q=maintenance_q,
            plant_store=germination_station,
            transport=transport,
            expense=self.expense,
            **config["maintenance"]
        )


if __name__ == "__main__":
    import yaml
    from pprint import pprint

    stream = open("config2.yaml", 'r')
    dictionary = yaml.safe_load(stream)
    pprint(dictionary, depth=3)

    sim = Simulation(None, dictionary["sim_details"])

    print(f"Revenue Total: {sim.revenue.total}")
    print(f"Expense Total: {sim.expense.total}")