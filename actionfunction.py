from distributions import Distribution
from factory import Simulation

class ActionFunction:

    def __init__(self, customer_change, build_change) -> None:
        self.cc = customer_change
        self.bc = build_change

        cac = [
            Distribution(**self.cc["cac"]["cac_low"]).get_single(),
            Distribution(**self.cc["cac"]["cac_med"]).get_single(),
            Distribution(**self.cc["cac"]["cac_high"]).get_single(),
        ]

        self.cc["cac"] = cac
        self.phase = 1
        self.changed_customer = False

    def __call__(self, sim: Simulation, step) -> dict:
        MRR = sim.active_clients.active_units*sim.active_clients.subscription_price
        builds = [x["sale"] for x in sim.revenue.record]
        actions = self.action_base
        if not self.changed_customer and MRR > self.cc["MRR_threshold"]:
            actions["customer_change"] = self.cc
            actions["customer_change"]["steps"] = step
            self.changed_customer = True
        
        if step > self.bc["rolling_average"] \
            and sum(builds[-self.bc["rolling_average"]:]) \
            > self.bc["rolling_average"]*self.bc["unit_threshold"]:
            self.phase = 2

        return actions

    @property
    def action_base(self):
        return {"phase":self.phase,"add_new_shelves":0,"plot_maintenance":None, "customer_change":None} 