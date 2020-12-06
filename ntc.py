import Adafruit_BBIO.ADC as ADC
import time
import math

kel = 273.15
beta=4060.
R0=100000.
T0 = 25. + kel

class Ntc():

    def __init__(self,pin):
        self.val = 0.0
        self.tempList = []
        self.pin=pin
        ADC.setup()


    def getVal(self):
        return self.val


    def update(self):
        t = 0
        for i in range(5):
            adc = ADC.read(self.pin)
            r = adc / (1. - adc) * 50000.
            t += 1.0 / (1.0 / T0 + (1.0 / beta) * math.log(r / R0)) - kel
            time.sleep(0.1)
        self.tempList.append(t/5)
        if len(self.tempList) > 5:
            del self.tempList[0]
        tSum = 0
        for t in self.tempList:
            tSum = tSum + t
        self.val = tSum / len(self.tempList)



