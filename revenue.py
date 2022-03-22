from logging import getLogger, INFO
from queue import Queue

class Revenue:
    """ All revenue generating activities go through here. 
        Basically clients make calls to this object when renewing subscriptions and 
        buying units. Keeps track of all the revenue generated, at what time"""
    

    def __init__(self, build_q: Queue, maintenance_q: Queue) -> None:
        self.payments = {
            "total":0,
            "sale":0,
            "subscription":0,
            "transactions":0
        }
        self.logger = getLogger(__name__)

        self.record = []

        self.build_q = build_q
        self.maintenance_q = maintenance_q

    def step(self, actions):
        self.record.append(self.payments)
        self.zero_payments()



    def make_payment(self, name, tag, amount, details):
        # print(f"\t{tag}\t{name}\t{amount}")
        self.payments["total"] += amount
        self.payments[tag] += amount
        self.payments["transactions"] += 1
        
        self.logger.log(INFO, f'REVENUE:{{"name":"{name}", "tag":"{tag}", "amount":{amount}, "details":{details}}}')

        if tag == "sale":
            self.build_q.put(details)
        elif tag == "subscription":
            self.maintenance_q.put(details)

    def zero_payments(self):
        self.payments = {
            "total":0,
            "sale":0,
            "subscription":0,
            "transactions":0
        }

    @property
    def total(self):
        return sum([x["total"] for x in self.record]) + self.payments["total"]

    @property
    def total_detailed(self):
        return {k:sum([x[k] for x in self.record]) for k in self.payments.keys()}