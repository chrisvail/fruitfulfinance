from queue import Queue
from expense import Expense


class BuildUnit:

    def __init__(self, man_cost, mat_cost, build_thresholds, phase_change, build_q: Queue, install_q: Queue, expense: Expense, phase=1) -> None:
        self.manufacture_costs = man_cost
        self.material_costs = mat_cost
        self.thresholds = build_thresholds

        self.phase_change = phase_change

        self.build_q = build_q
        self.expense = expense
        
        self.install_q = install_q
        # Add delay of 2 weeks
        self.install_q.put([])
        self.install_q.put([])

        self.phase = phase

    def step(self, actions):
        builds = []
        unit_total = 0
        while not self.build_q.empty():
            build_req = self.build_q.get()
            builds.append(build_req)
            unit_total += build_req["units"]

        if self.phase == 2:
            manufacture_total = unit_total*self.manufacture_costs[-1]
            materials_total = unit_total*self.material_costs[-1]
        elif self.phase == 1:
            curr_threshold = self.get_threshold(unit_total)
            
            manufacture_total = unit_total*self.manufacture_costs[0][curr_threshold]
            materials_total = unit_total*self.material_costs[0][curr_threshold]

        # Expense materials and manufacture separately for record purposes
        self.expense.make_payment(
            name="manufacturing",
            tag="build",
            amount=manufacture_total,
            details={"units":unit_total}
        )
        self.expense.make_payment(
            name="materials",
            tag="build",
            amount=materials_total,
            details={"units":unit_total}
        )

        # Takes 2 weeks to build and prep for install
        client_list = [x["client"] for x in builds]
        self.install_q.put(client_list)

        if self.phase != actions["phase"]:
            self.phase = actions["phase"]
            self.expense.make_payment(
                "phase capex",
                "build",
                amount=self.phase_change
            )

    def get_threshold(self, units):

        for i, threshold in enumerate(self.thresholds):
            if units > threshold:
                continue
            else:
                return i
        return -1
            