import Adafruit_BBIO.ADC as ADC
import time

class pt100():

    def __init__(self, gpio):
        self.gpio=gpio
        self.val=0.0
        self.tempList=[]
        ADC.setup()

    def getVal(self):
        return self.val


    def update(self):
        value=0
        for i in range(10):
                value = value + ADC.read(self.gpio)
                time.sleep(0.01)		
        value = value / 10.
        self.tempList.append((value * 1.8 / 81.6 -0.004) /0.016 * 200)
        if len(self.tempList)> 5:
            del self.tempList[0]
        tSum=0
        for t in self.tempList:
            tSum=tSum+t
        self.val= tSum/len(self.tempList)
