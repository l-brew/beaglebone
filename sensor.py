from abc import ABC, abstractmethod

class Sensor(ABC):
    def __init__(self):
        self.val=0

    def getVal(self):
        return self.val

    @abstractmethod
    def update(self):
        pass
