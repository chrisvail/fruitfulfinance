from queue import Queue
from time import perf_counter
import pandas as pd
from matplotlib import pyplot as plt

from buildInstall.build import BuildUnit
from buildInstall.install import InstallUnits
from customerAquisition.activeclients import ActiveClients
from customerAquisition.customerAcquisition import CustomerAcquisition
from germination.germinationStation import GerminationStation
from maintenance.maintenance import Maintenance
from shared.transport import Transport
from expense import Expense
from revenue import Revenue
from operationCost import OperationCost
from distributions import Distribution
from clock import SimClock

from customerAquisition.client import Client



class Simulation:

    def __init__(self, sim_details, steps, action_function=None) -> None:
        self.startup_time = {}
        # Create clock for the simulation
        t0 = perf_counter()
        self.sim_clock = SimClock()
        self.record = []

        if action_function is None:
            self.action_function = lambda self, step: {"phase":1,"add_new_shelves":0,"plot_maintenance":None} 
        else:
            self.action_function = action_function

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

        # Create op_cost
        self.operations = OperationCost(expense=self.expense, **sim_details["op_cost"])

        # Create transportation
        t0 = perf_counter()
        transport = Transport(**sim_details["transport"])
        self.startup_time["Trasport"] = perf_counter() - t0
        # Create germination station
        t0 = perf_counter()
        self.germination_station = GerminationStation(
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

        self.active_clients = ActiveClients(
            revenue=self.revenue, 
            expense=self.expense, 
            plant_requester=self.germination_station,
            **sim_details["activeClients"]
        )

        self.customer_acquisition = CustomerAcquisition(
            activeClients=self.active_clients,
            **sim_details["customerAcquisition"]
        )
        self.startup_time["Customer"] = perf_counter() - t0
        # Build system
        t0 = perf_counter()
        self.build = BuildUnit(
            expense=self.expense,
            build_q=build_q,
            install_q=install_q,
            **sim_details["build"]
        )

        self.install = InstallUnits(
            transport=transport,
            install_q=install_q,
            expense=self.expense,
            plant_store=self.germination_station,
            **sim_details["install"]
        )
        self.startup_time["Build"] = perf_counter() - t0

        # Maintenance
        t0 = perf_counter()
        self.maintenance = Maintenance(
            maintenance_q=maintenance_q,
            plant_store=self.germination_station,
            transport=transport,
            expense=self.expense,
            **sim_details["maintenance"]
        )
        self.startup_time["Maintenance"] = perf_counter() - t0
        # Add objects to the simulation clock
        t0 = perf_counter()
        self.sim_clock.subscribe(self.active_clients)
        self.sim_clock.subscribe(self.customer_acquisition)
        self.sim_clock.subscribe(self.revenue)
        self.sim_clock.subscribe(self.build)
        self.sim_clock.subscribe(self.install)
        self.sim_clock.subscribe(self.maintenance)
        self.sim_clock.subscribe(self.germination_station)
        self.sim_clock.subscribe(self.expense)

        self.startup_time["Subscription"] = perf_counter() - t0

    def run(self):
        for i in range(self.steps):
            actions = self.action_function(self, i)         
            self.sim_clock.step(actions)
            self.make_record()
        

    def make_record(self):
        # Cashflow
        # Active units 
        # MARR
        record = {
            "expenses_total": self.expense.record[-1]["total"],
            "expenses_customer_acquisition": self.expense.record[-1]["customer_acquisition"],
            "expenses_build": self.expense.record[-1]["build"],
            "expenses_maintenance": self.expense.record[-1]["maintenance"],
            "expenses_germination": self.expense.record[-1]["germination"],
            "expenses_op_cost": self.expense.record[-1]["op_cost"],
            "expenses_transactions": self.expense.record[-1]["transactions"],
            "revenue_total": self.revenue.record[-1]["total"],
            "revenue_sale": self.revenue.record[-1]["sale"],
            "revenue_subscription": self.revenue.record[-1]["subscription"],
            "revenue_transactions": self.revenue.record[-1]["transactions"],
            "client_count":len(self.active_clients.clients),
            "active_units": sum([x.unit_count for x in self.active_clients.clients]),
            "average_lifetime": sum([x.client_lifetime for x in self.active_clients.clients])/max([len(self.active_clients.clients), 1]),
            "churned":self.active_clients.churned
        }

        self.record.append(record)
        

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

        # print("\tStart up")
        # startup_total = sum([x for x in sim.startup_time.values()])
        # for key, value in sim.startup_time.items():
        #     print(f"\t\t{key}:\t{value}\t{value/startup_total*100:.2f}%")

        # step_total = sum([x for x in sim.sim_clock.get_times().values()]) 
        # print("\tStepping")
        # for key, value in sim.sim_clock.get_times().items():
        #     print(f"\t\t{key}:\t{value}\t{value/step_total*100:.2f}%")

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

        df = pd.DataFrame(sim.record)

        print(df)
        df.to_csv(f"{dictionary['name']}{i}.csv")
        df.plot.line(y=["client_count", "active_units"])
        df.plot.line(y=["client_count", "churned"])

        plt.show()

    print(sum(times))
