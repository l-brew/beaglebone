import threading
import pid
import Adafruit_BBIO.GPIO as GPIO
import sensor

class relay_ctrl():

    def __init__(self,pid,sensor,gpioH,gpioC,period=10):
        self.setPoint=50
        self.gpioH=gpioH
        self.gpioC=gpioC
        self.tmp=0
        self.period=period
        GPIO.setup(self.gpioH,GPIO.OUT)
        GPIO.setup(self.gpioC,GPIO.OUT)
        self.sensor=sensor
        self.pid=pid
        self.ctlOn=False

    def setServer(self,server):
        self.server=server

    def on(self):
        if self.ctlOn==False:
            return
        # perf=timer.perf_counter()

        if(self.pid.getCtlSig()!=0):
            if self.pid.getCtlSig() > 0 :
                GPIO.output(self.gpioH,GPIO.HIGH)
                GPIO.output(self.gpioC,GPIO.LOW)
            else:
                GPIO.output(self.gpioC,GPIO.HIGH)
                GPIO.output(self.gpioH,GPIO.LOW)
            self.onDelay=abs(self.pid.getCtlSig())/100.*self.period
            self.offDelay=self.period-self.onDelay
            if (self.onDelay< self.period):
                self.timer = threading.Timer(self.onDelay, self.off) 
                self.timer.start()
            else :
                self.onDelay=self.period
                self.timer = threading.Timer(self.period, self.on)
                self.timer.start()
        else:
            GPIO.output(self.gpioH,GPIO.LOW)
            GPIO.output(self.gpioC,GPIO.LOW)
            self.timer = threading.Timer(self.period, self.on)
            self.timer.start()
        self.server.update()

    def off(self):
        if self.ctlOn==False:
            return
        GPIO.output(self.gpioH,GPIO.LOW)
        GPIO.output(self.gpioC,GPIO.LOW)
        self.timer = threading.Timer(self.offDelay, self.on)
        self.timer.start()
        self.server.update()

        # self.ctlSig


    def run(self):
        if self.ctlOn==False:
            self.ctlOn=True
            self.on()

    def getPeriod(self):
        return self.period

    def setPeriod(self, period):
        self.period=period 


    def stop(self):
        self.timer.cancel()
        self.ctlOn=False

    def isRunning(self):
        return self.ctlOn

    def coolerOn(self):
        GPIO.output(self.gpioC,GPIO.HIGH)

    def coolerOff(self):
        GPIO.output(self.gpioC,GPIO.LOW)

    def heaterOn(self):
        GPIO.output(self.gpioH,GPIO.HIGH)

    def heaterOff(self):
        GPIO.output(self.gpioH,GPIO.LOW)

    def allOff(self):
        GPIO.output(self.gpioC,GPIO.LOW)
        GPIO.output(self.gpioH,GPIO.LOW)

    def coolerIsOn(self):
        return bool(GPIO.input(self.gpioC))

    def heaterIsOn(self):
        return bool(GPIO.input(self.gpioH))
