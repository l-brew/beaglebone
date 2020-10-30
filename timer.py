import time
import threading
class timer:

    def __init__(self):
        self.isRunning=False
        self.startTime=0
        self.setTime=0
        self.terminateAlarm=True

    def setTimer(self,time):
        if self.isRunning:
            return
        self.setTime=time

    def start(self):
        if self.isRunning:
            return
        self.timer = threading.Timer(self.setTime, self.alarm)
        self.timer.start()
        self.isRunning=True

    def stop(self):
        try:
            self.timer.cancel()
        except:
            pass
        self.isRunning=False

    def isAlarm(self):
        return not self.terminateAlarm

    def terminate(self):
        self.terminateAlarm=True

    def alarm(self):
        self.terminateAlarm=False
        while not self.terminateAlarm:
            print("alarm")
            time.sleep(1)
        self.isRunning=False

