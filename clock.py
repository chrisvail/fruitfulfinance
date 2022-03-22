from logging import getLogger
from time import perf_counter

class SimClock:

    def __init__(self) -> None:
        self.subscribers = []
        self._step = 0
        self.logger = getLogger(__name__)
        self.logger.info("Starting step: 0")
    
        self.times = {}

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
        self.times[type(subscriber).__name__] = []

    def step(self, actions):
        self._step += 1
        self.logger.info(f"Starting step: {self._step}")
        for sub in self.subscribers:
            t0 = perf_counter()
            sub.step(actions)
            self.times[type(sub).__name__].append(perf_counter() - t0)

    def get_times(self):
        return {k:sum(v)/len(v) for k, v in self.times.items()}