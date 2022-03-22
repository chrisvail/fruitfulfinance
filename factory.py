from queue import Queue
from time import perf_counter

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

from customerAquisition.client import Client



class Simulation:

    def __init__(self, sim_details, steps) -> None:
        self.startup_time = {}
        # Create clock for the simulation
        t0 = perf_counter()
        self.sim_clock = SimClock()

        self.steps = steps

        # Create queues for passing information
        build_q = Queue()
        install_q = Queue()
        maintenance_q = Queue()
        self.startup_time["Misc"] = perf_counter() - t0

        # Build cashflow capture
        t0 = perf_counter()
        self.expense = Expense()
        self.revenue = Revenue(build_q, maintenance_q)
        self.startup_time["Cashflow"] = perf_counter() - t0

        # Create transportation
        t0 = perf_counter()
        transport = Transport(**sim_details["transport"])
        self.startup_time["Trasport"] = perf_counter() - t0
        # Create germination station
        t0 = perf_counter()
        germination_station = GerminationStation(
            expense=self.expense, 
            **sim_details["germinationStation"]
        )
        self.startup_time["Germination"] = perf_counter() - t0


        # Customer Acquisition System
        # Create simulation cac values
        t0 = perf_counter()
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
        self.startup_time["Customer"] = perf_counter() - t0
        # Build system
        t0 = perf_counter()
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
        self.startup_time["Build"] = perf_counter() - t0

        # Maintenance
        t0 = perf_counter()
        maintenance = Maintenance(
            maintenance_q=maintenance_q,
            plant_store=germination_station,
            transport=transport,
            expense=self.expense,
            **sim_details["maintenance"]
        )
        self.startup_time["Maintenance"] = perf_counter() - t0
        # Add objects to the simulation clock
        t0 = perf_counter()
        self.sim_clock.subscribe(active_clients)
        self.sim_clock.subscribe(customer_acquisition)
        self.sim_clock.subscribe(self.revenue)
        self.sim_clock.subscribe(build)
        self.sim_clock.subscribe(install)
        self.sim_clock.subscribe(maintenance)
        self.sim_clock.subscribe(germination_station)
        self.sim_clock.subscribe(self.expense)

        self.startup_time["Subscription"] = perf_counter() - t0

    def run(self):
        actions = {
            "phase":1,
            "add_new_shelves":0,
            "plot_maintenance":None
        }            
        times = []
        for i in range(self.steps):
            # print(f"Step {i}")
            if i == 100:
                actions["plot_maintenance"] = "testplot_sim"
            t0 = perf_counter()
            self.sim_clock.step(actions)
            times.append(perf_counter() - t0)
            if i == 100:
                actions["plot_maintenance"] = None
        # print(sum(times)/len(times))
        

if __name__ == "__main__":
    import yaml
    from pprint import pprint

    stream = open("config2.yaml", 'r')
    dictionary = yaml.safe_load(stream)
    # pprint(dictionary)

    times = []

    for i in range(dictionary["runs"]):
        print(f"Run {i}", end="\t")
        t0 = perf_counter()
        sim = Simulation(dictionary["sim_details"], dictionary["steps"])
        sim.run()

        times.append(perf_counter() - t0)
        print(f"Time: {times[-1]}")

        print("\tStart up")
        startup_total = sum([x for x in sim.startup_time.values()])
        for key, value in sim.startup_time.items():
            print(f"\t\t{key}:\t{value}\t{value/startup_total*100:.2f}%")

        step_total = sum([x for x in sim.sim_clock.get_times().values()]) 
        print("\tStepping")
        for key, value in sim.sim_clock.get_times().items():
            print(f"\t\t{key}:\t{value}\t{value/step_total*100:.2f}%")

        rev = sim.revenue.total_detailed
        exp = sim.expense.total_detailed
        print(f"Revenue Total:")
        for k, v in rev.items():
            print(f"\t{k}:\t{v:.2f}\t{v/rev['total']*100:.2f}%")

        print(f"Expense Total:")
        for k, v in exp.items():
            print(f"\t{k}:\t{v:.2f}\t{v/exp['total']*100:.2f}%")
        
        print(f"Client Count:\t{Client.client_count}")
        print(f"Client Churn:\t{Client.client_churned}")

    print(sum(times))
