from logging import getLogger

class SimClock:

    def __init__(self) -> None:
        self.subscribers = []
        self._step = 0
        self.logger = getLogger(__name__)
        self.logger.info("Starting step: 0")
    
    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def step(self, actions):
        self._step += 1
        self.logger.info(f"Starting step: {self._step}")
        for sub in self.subscribers:
            sub.step(actions)