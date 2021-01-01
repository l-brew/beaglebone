import Adafruit_BBIO.GPIO as GPIO
from Adafruit_BBIO.SPI import SPI
import time
from bisect import bisect_right
from sensor import Sensor

CS_PIN= 'P9_25'

REG_CONF = 0x80
REG_MSB = 0x01
REG_LSB = 0x02

CNF_ONESHOT = 0b10100011

CNF_IDLE = 0b00000011

y=(-220 , -200 , -180 , -160 , -140 , -120 , -100 , -80 , -60 , -40 ,
-30 , -20 , -10 , 0 , 10 , 20 , 30 , 40 , 50 , 60 , 80 ,
100 , 120 , 140 , 160 , 180 , 200 , 220 , 240 , 260 , 280 , 300 ,
320 , 340 , 360 , 380 , 400 , 420 , 440 , 460 , 480 , 500 , 520 ,
540 , 560 , 580 , 600 , 620 , 640 , 660 , 700 , 750)

x=(10.41, 18.53, 27.05, 35.48, 43.80, 52.04, 60.20, 68.28, 76.28, 84.21, 88.17,
92.13, 96.07, 100.00, 103.90, 107.79, 111.67, 115.54, 119.40, 123.24, 130.89, 138.50,
146.06, 153.57, 161.04, 168.47, 175.84, 183.17, 190.46, 197.70, 204.88, 212.03, 219.13,
226.18, 233.19, 240.15, 247.06, 253.93, 260.75, 267.52, 274.25, 280.93, 287.57, 294.16,
300.70, 307.20, 313.65, 320.05, 326.41, 332.72, 345.21, 360.55)


class Interpolate:
    def __init__(self, x_list, y_list):
        if any(y - x <= 0 for x, y in zip(x_list, x_list[1:])):
            raise ValueError("x_list must be in strictly ascending order!")
        self.x_list = x_list
        self.y_list = y_list
        intervals = zip(x_list, x_list[1:], y_list, y_list[1:])
        self.slopes = [(y2 - y1) / (x2 - x1) for x1, x2, y1, y2 in intervals]

    def __call__(self, x):
        if not (self.x_list[0] <= x <= self.x_list[-1]):
            raise ValueError("x out of bounds!")
        if x == self.x_list[-1]:
            return self.y_list[-1]
        i = bisect_right(self.x_list, x) - 1
        return self.y_list[i] + self.slopes[i] * (x - self.x_list[i])
    
    

class PT100(Sensor):

    def __init__(self):
        self.val=None
        self.tempList=[]
        self.spi = SPI(0, 0)
        self.spi.msh=1000000
        GPIO.setup(CS_PIN,GPIO.OUT)
        GPIO.output(CS_PIN,GPIO.HIGH)
        self.inter=Interpolate(x,y)
    
    def spi_read(self):
        GPIO.output(CS_PIN,GPIO.LOW)
        self.spi.xfer([REG_CONF,CNF_ONESHOT])
        GPIO.output(CS_PIN,GPIO.HIGH)
        time.sleep(0.1)
        
        GPIO.output(CS_PIN,GPIO.LOW)
        self.spi.xfer([REG_LSB])
        lsb=self.spi.readbytes(1)
        GPIO.output(CS_PIN,GPIO.HIGH)
        
        GPIO.output(CS_PIN,GPIO.LOW)
        self.spi.xfer([REG_MSB])
        msb=self.spi.readbytes(1)
        GPIO.output(CS_PIN,GPIO.HIGH)
        
        err=(False,True)[lsb[0]&1]
        
        adc=(msb[0]<<8|lsb[0])>>1
        return (err,adc)


    def update(self):
        value=0
        err=False
        for i in range(10):
                err,adc = self.spi_read()
                if err:
                    break
                value = value + adc
        if err:
            #self.val=None
            return
        value = value / 10.
        
        res=(value/2**15*400)
        
        self.tempList.append(self.inter(res))
        if len(self.tempList)> 5:
            del self.tempList[0]
        tSum=0
        for t in self.tempList:
            tSum=tSum+t
        self.val= tSum/len(self.tempList)
