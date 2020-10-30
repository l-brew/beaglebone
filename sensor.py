from abc import ABC, abstractmethod

class sensor(ABC):
    @abstractmethod
    def sensor(self):
        pass

    @abstractmethod
    def getVal(self):
        pass
