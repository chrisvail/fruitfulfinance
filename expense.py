from logging import getLogger, INFO
from queue import Queue

class Expense:
    """ All expense generating activities go through here. 
        Whenever we pay for anything it goes through here"""
    

    def __init__(self) -> None:
        self.payments = {
            "total":0,
            "customer_acquisition":0,
            "build":0,
            "maintenance":0,
            "germination":0,
            "op_cost":0,
            "capex":0,
            "transactions":0
        }
        self.logger = getLogger(__name__)

        self.record = []


    def step(self, actions):
        self.make_record()

    def make_record(self):
        self.record.append(self.payments)
        self.zero_payments()



    def make_payment(self, name, tag, amount, details={}):
        # print(f"\t{tag}\t{name}\t-{amount}")
        self.payments["total"] += amount
        self.payments[tag] += amount
        if "capex" in name:
            self.payments["capex"] += amount
        self.payments["transactions"] += 1
        
        self.logger.log(INFO, f'EXPENSE:{{"name":"{name}", "tag":"{tag}", "amount":{amount}, "details":{details}}}')


    def zero_payments(self):
        self.payments = {
            "total":0,
            "customer_acquisition":0,
            "build":0,
            "maintenance":0,
            "germination":0,
            "op_cost":0,
            "capex":0,
            "transactions":0
        }

    @property
    def total(self):
        return sum([x["total"] for x in self.record]) + self.payments["total"]

    
    @property
    def total_detailed(self):
        return {k:sum([x[k] for x in self.record]) for k in self.payments.keys()}