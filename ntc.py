import Adafruit_BBIO.ADC as ADC
import time
import math
from sensor import Sensor

KEL = 273.15
BETA=4060.
R0=100000.
T0 = 25. + KEL

class Ntc(Sensor):

    def __init__(self,pin,beta=BETA,r0=R0,t0=T0):
        self.val = 0.0
        self.tempList = []
        self.pin=pin
        self.beta=beta
        self.r0=r0
        self.t0=t0
        ADC.setup()


    def update(self):
        t = 0
        for i in range(5):
            adc = ADC.read(self.pin)
            r = adc / (1. - adc) * 50000.
            t += 1.0 / (1.0 / self.t0 + (1.0 / self.beta) * math.log(r / self.r0)) - KEL
            time.sleep(0.1)
        self.tempList.append(t/5)
        if len(self.tempList) > 5:
            del self.tempList[0]
        tSum = 0
        for t in self.tempList:
            tSum = tSum + t
        self.val = tSum / len(self.tempList)



