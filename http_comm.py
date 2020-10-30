import sys, os
import time
import subprocess
#from flup.server.fcgi import WSGIServer
from _thread import start_new_thread
import cgi
from relay_ctrl import relay_ctrl
from pid import pid
import threading
from urllib.parse import urlencode, quote_plus

import http.client
import ssl
import time
import json

SERVER_ADDRESS = 'laubersberg.de'

class http_comm:
    def __init__(self, pid, ctl, sensor, start, logger, stirrer,tilt):
        global SERVER_ADDRESS
        self.stirrer=stirrer
        self.pid=pid
        self.ctl=ctl
        self.sensor=sensor
        self.start=start
        self.logger=logger
        self.sslContext = ssl.create_default_context()
        self.lock = threading.Lock()
        self.tilt=tilt

    def run(self):
        threading.Thread(target = self.fullStatus ).start()
        threading.Thread(target = self.listenToServer).start()
        threading.Thread(target = self.sendTimer).start()

    def update(self):
        try:
            self.lock.release()
        except RuntimeError:
            pass


    def sendTimer(self):
        while True:
            self.update()
            time.sleep(4)


    def listenToServer(self):
        while True:
            try:
                conn = http.client.HTTPSConnection(SERVER_ADDRESS, context=self.sslContext)
                conn.request("GET", "/brewserver/commands/listen/")
                r1 = conn.getresponse()
                form = json.loads(r1.read().decode('utf-8'))
                if "ramp" in form.keys():
                        self.start.setRamp(float(escape(form["ramp"])))
                        writeConfig=True
                if "soll" in form.keys():
                    self.start.setSetPoint(float(escape(form["soll"])))
                    writeConfig=True
                if "k_p" in form.keys():
                    self.pid.setK_p(float(escape(form["k_p"])))
                    writeConfig=True
                if "k_i" in form.keys():
                    self.pid.setK_i(float(escape(form["k_i"])))
                    writeConfig=True
                if "freeze" in form.keys():
                    if form["freeze"] == "true":
                        self.pid.freeze()
                    if form["freeze"] == "false":
                        self.pid.unfreeze()
                if "i_err" in form.keys():
                    self.pid.setI_err(float(escape(form["i_err"]))/getK_i())
                if "period" in form.keys():
                    self.ctl.setPeriod(float(escape(form["period"])))
                if "reg" in form.keys():
                    if form["reg"] == "on" :
                       self.ctl.run() 
                    elif form["reg"] == "off" :
                        self.ctl.stop()
                        self.ctl.allOff()
                if "cooler" in form.keys():
                    if form["cooler"] == "on" :
                        self.ctl.stop()
                        self.ctl.coolerOn()
                    if form["cooler"] == "tgl" :
                        self.ctl.stop()
                        if self.ctl.coolerIsOn():
                            self.ctl.coolerOff()
                        else:
                            self.ctl.coolerOn()
                    elif form["cooler"] == "off" :
                        self.ctl.coolerOff()
                if "heater" in form.keys():
                    if form["heater"] == "on" :
                        self.ctl.stop()
                        self.ctl.heaterOn()
                    if form["heater"] == "tgl" :
                        self.ctl.stop()
                        if self.ctl.heaterIsOn():
                            self.ctl.heaterOff()
                        else:
                            self.ctl.heaterOn()
                    elif form["heater"] == "off" :
                        self.ctl.heaterOff()
                if "stirrer" in form.keys():
                    if form["stirrer"] == "off" :
                        self.stirrer.stop()
                    else:
                        try:
                            self.stirrer.start(float(form["stirrer"]))
                        except :
                            pass
                if "rampUp" in form.keys():
                    print("ramp Up")
                    self.pid.setSetPoint(self.sensor.getVal())
                    self.ctl.run() 

                if "reset" in form.keys():
                    if form["reset"] == "true" :
                       self.pid.setI_err(0)
                if "setI" in form.keys():
                   self.pid.setI_err(float(form["setI"])/self.pid.getK_i())
                if "plotMinutes" in form.keys():
                        regler.plotSeconds
                if "rampup2" in form.keys():
                    # ramp up to value in specified time
                    minutes=float(form["rampup2"]["minutes"])
                    temp=float(form["rampup2"]["temp"])
                    cur_val=self.pid.getSetPoint()
                    print(minutes,temp)
                    if cur_val != temp:
                        if minutes== 0 :
                            self.start.setRamp(0)
                            self.start.setSetPoint(temp)
                            self.pid.setSetPoint(temp)
                        else:
                            ramp=abs(temp-cur_val)/minutes
                            self.start.setRamp(ramp)
                            self.start.setSetPoint(temp)

                self.update()

                if writeConfig :
                    self.start.getCtlConfig()["SetPoint"]=str(self.start.getSetPoint())
                    self.start.getCtlConfig()["K_p"]=str(self.pid.getK_p())
                    self.start.getCtlConfig()["K_i"]=str(self.pid.getK_i())
                    self.start.writeConfig()


               
            except:
                time.sleep(1)
                        
    
    def fullStatus(self):
        
        while True:
            power = self.pid.getCtlSig()
            if power > 100:
                power = 100
            elif power < -100:
                power = -100

            data = {
            'time': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),
            'temp': self.sensor.getVal(),
            'set_point': self.pid.getSetPoint(),
            'k_i': self.pid.getK_i(),
            'k_p': self.pid.getK_p(),
            'plotMinutes' : 0,#regler.plotSeconds/60,
            'actuating_value' : self.pid.getCtlSig(),
            'err' :self.pid.getErr()*self.pid.getK_p(),
            'i_err' : self.pid.getI_err()*self.pid.getK_i(),
            'heater' :self.ctl.heaterIsOn(),
            'cooler' :self.ctl.coolerIsOn(),
            'stirrer' :self.stirrer.isRunning(),
            'power' :power,#regler.power,
            'reg' :self.ctl.isRunning(),
            'ramp' :self.start.getRamp(),
            'target' :self.start.getTarget(),
            'period' :self.ctl.getPeriod(),
            'frozen' :self.pid.getFrozen(),
            'tilt_temp' : self.tilt.temp,
            'tilt_grav' : self.tilt.grav
                }

            #try:
            if True:
                conn = http.client.HTTPSConnection(SERVER_ADDRESS, context=self.sslContext)
                body=urlencode(data,quote_via=quote_plus)
                conn.request("POST", "/brewserver/status/update/",headers={"Content-Type":"application/x-www-form-urlencoded"},body=body)
                r1 = conn.getresponse()
                f=open("response.html","w")
                f.write(r1.read().decode('utf-8'))
                f.close()
            #except:
            #    continue
            # print(r1.status, r1.reason)
            self.lock.acquire()

def escape(s):
    return s


