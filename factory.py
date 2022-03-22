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
from clock import SimClock



class Simulation:

    def __init__(self, sim_details, steps) -> None:
        # Create clock for the simulation
        self.sim_clock = SimClock()

        self.steps = steps

        # Create queues for passing information
        build_q = Queue()
        install_q = Queue()
        maintenance_q = Queue()

        # Build cashflow capture
        self.expense = Expense()
        self.revenue = Revenue(build_q, maintenance_q)

        # Create transportation
        transport = Transport(**sim_details["transport"])

        # Create germination station
        germination_station = GerminationStation(
            expense=self.expense, 
            **sim_details["germinationStation"]
        )


        # Customer Acquisition System
        # Create simulation cac values
        cac_low = Distribution(**sim_details["cac"]["cac_low"]).get_single()
        cac_med = Distribution(**sim_details["cac"]["cac_med"]).get_single()
        cac_high = Distribution(**sim_details["cac"]["cac_high"]).get_single()
        sim_details["activeClients"]["cac"]["values"] = [cac_low, cac_med, cac_high]

        active_clients = ActiveClients(
            revenue=self.revenue, 
            expense=self.expense, 
            plant_requester=germination_station,
            **sim_details["activeClients"]
        )

        customer_acquisition = CustomerAcquisition(
            activeClients=active_clients,
            **sim_details["customerAcquisition"]
        )

        # Build system
        build = BuildUnit(
            expense=self.expense,
            build_q=build_q,
            install_q=install_q,
            **sim_details["build"]
        )

        install = InstallUnits(
            transport=transport,
            install_q=install_q,
            expense=self.expense,
            plant_store=germination_station,
            **sim_details["install"]
        )

        # Maintenance
        maintenance = Maintenance(
            maintenance_q=maintenance_q,
            plant_store=germination_station,
            transport=transport,
            expense=self.expense,
            **sim_details["maintenance"]
        )

        # Add objects to the simulation clock
        self.sim_clock.subscribe(active_clients)
        self.sim_clock.subscribe(customer_acquisition)
        self.sim_clock.subscribe(self.revenue)
        self.sim_clock.subscribe(build)
        self.sim_clock.subscribe(install)
        self.sim_clock.subscribe(maintenance)
        self.sim_clock.subscribe(germination_station)
        self.sim_clock.subscribe(self.expense)

    def run(self):
        actions = {

        }
        for _ in range(self.steps):
            self.sim_clock.step(actions)
        
        

if __name__ == "__main__":
    import yaml
    from pprint import pprint

    stream = open("config2.yaml", 'r')
    dictionary = yaml.safe_load(stream)
    pprint(dictionary, depth=3)

    sim = Simulation(dictionary["sim_details"], dictionary["steps"])
    sim.run()


    print(f"Revenue Total: {sim.revenue.total}")
    print(f"Expense Total: {sim.expense.total}")