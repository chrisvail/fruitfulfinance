from logging import getLogger, INFO
from queue import Queue

class Expense:
    """ All expense generating activities go through here. 
        Whenever we pay for anything it goes through here"""
    

    def __init__(self) -> None:
        self.payments = {
            "total":0,
            "customer acquisition":0,
            "build":0,
            "maintenance":0,
            "germination":0,
            "transactions":0
        }
        self.logger = getLogger(__name__)

        self.step = 0
        self.record = []


    def step(self, actions):
        self.record.append(self.payments)
        self.zero_payments()
        self.step += 1


    def make_payment(self, name, tag, amount, details={}):
        self.payments["total"] += amount
        self.payments[tag] += amount
        self.payments["transactions"] += 1
        
        self.logger.log(INFO, f'EXPENSE:{{"name":"{name}", "tag":"{tag}", "amount":{amount}, "details":{details}}}')


    def zero_payments(self):
        self.payments = {
            "total":0,
            "customer acquisition":0,
            "build":0,
            "maintenance":0,
            "germination":0,
            "transactions":0
        }

    @property
    def total(self):
        return sum([x["total"] for x in self.record]) + self.payments["total"]