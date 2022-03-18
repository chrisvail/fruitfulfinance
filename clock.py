

class SimClock:

    def __init__(self) -> None:
        self.subscribers = []
        self.step = 0

    
    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def step(self, actions):
        for sub in self.subscribers:
            sub.notify(actions)