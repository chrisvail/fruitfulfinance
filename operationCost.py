from distributions import Distribution
from expense import Expense

class OperationCost:

    def __init__(self, op_cost_dist, expense:Expense) -> None:
        self.op_cost = Distribution(**op_cost_dist)
        self.expense = expense

    def step(self, action):
        self.expense.make_payment(
            name="op_cost",
            tag="op_cost",
            amount=self.op_cost.get_single()
        )