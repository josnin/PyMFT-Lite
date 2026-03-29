from abc import ABC, abstractmethod

class UnitOfWork(ABC):
    def __init__(self):
        self.seen_entities = set() # Track entities that may have events

    def __enter__(self): return self
    def __exit__(self, *args): self.rollback()

    @abstractmethod
    def commit(self): pass

    @abstractmethod
    def rollback(self): pass

    def collect_new_events(self):
        """Pulls events out of domain objects to be processed by the bus."""
        for entity in self.seen_entities:
            while entity.events:
                yield entity.events.pop(0)
