import threading
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time
class stirrer:
    def __init__(self,gpio):
        self.gpio=gpio
        self.duty = 0
        self.freq = 20000
        self.rampLock=False

    def ramp(self,duty):
        if duty > 100:
            duty = 100
        if self.rampLock:
            return
        self.rampLock=True
        direct = 0
        if (duty > self.duty):
            direct = 1
        else :
            direct = -1

        while (duty-self.duty)*direct>0:
            self.duty=self.duty+direct*2
            try:
                PWM.start(self.gpio,self.duty*0.7,self.freq)
            except:
                pass
            time.sleep(0.1)
        self.rampLock=False

    def start(self,duty):
        if duty > 100:
            duty = 100
        if duty < 0:
            duty = 0
        threading.Thread(target=self.ramp,args=(duty,)).start()

    def stop(self):
        threading.Thread(target=self.ramp,args=(0,)).start()
        
    def play(self,tune):
        threading.Thread(target=self.tuneThread,args=(tune,)).start()

    def tuneThread(self,tune):
        for t in tune:
            if t[0] == 0 :
                t[0] = 20000
            try:
                PWM.start(self.gpio,self.duty*0.7,t[0])
            except:
                pass
            time.sleep(t[1])

    def isRunning(self):
        if self.duty > 0 :
            return True
        else :
            return False


if __name__ == "__main__":
    st=stirrer("P9_28")
    st.start(50)
    st.play([[2093,0.1],
    [2637,0.1],
    [3136,0.1],
    [0,0]])
    time.sleep(1)
    st.play([[3136,0.1],
    [0,0.02],
    [3136,0.1],
    [0,0.02],
    [3136,0.1],
    [0,0]])
    time.sleep(1)
    st.stop()

