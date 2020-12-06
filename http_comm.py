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


class http_comm:
    def __init__(self, start):
        print("http init")
        self.start=start
        self.sslContext = ssl.create_default_context()
        self.lock = threading.Lock()
        self.server_address=start.serverConfig.get("server_address","localhost")
        print(self.server_address)
        print("http init end")

    def run(self):
        print('http run')
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
                conn = http.client.HTTPSConnection(self.server_address, context=self.sslContext)
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
                    self.start.pid1.setK_p(float(escape(form["k_p"])))
                    writeConfig=True
                if "k_i" in form.keys():
                    self.start.pid1.setK_i(float(escape(form["k_i"])))
                    writeConfig=True
                if "freeze" in form.keys():
                    if form["freeze"] == "true":
                        self.start.pid1.freeze()
                    if form["freeze"] == "false":
                        self.start.pid1.unfreeze()
                if "i_err" in form.keys():
                    self.start.pid1.setI_err(float(escape(form["i_err"]))/getK_i())
                if "period" in form.keys():
                    self.start.ctl1.setPeriod(float(escape(form["period"])))
                if "reg" in form.keys():
                    if form["reg"] == "on" :
                       self.start.ctl1.run()
                    elif form["reg"] == "off" :
                        self.start.ctl1.stop()
                        self.start.ctl1.allOff()
                if "cooler" in form.keys():
                    if form["cooler"] == "on" :
                        self.start.ctl1.stop()
                        self.start.ctl1.coolerOn()
                    if form["cooler"] == "tgl" :
                        self.start.ctl1.stop()
                        if self.start.ctl1.coolerIsOn():
                            self.start.ctl1.coolerOff()
                        else:
                            self.start.ctl1.coolerOn()
                    elif form["cooler"] == "off" :
                        self.start.ctl1.coolerOff()
                if "heater" in form.keys():
                    if form["heater"] == "on" :
                        self.start.ctl1.stop()
                        self.start.ctl1.heaterOn()
                    if form["heater"] == "tgl" :
                        self.start.ctl1.stop()
                        if self.start.ctl1.heaterIsOn():
                            self.start.ctl1.heaterOff()
                        else:
                            self.start.ctl1.heaterOn()
                    elif form["heater"] == "off" :
                        self.start.ctl1.heaterOff()
                if "stirrer" in form.keys():
                   
                    if form["stirrer"] == "off" :
                        self.start.stirrer1.stop()
                    else:
                        try:
                            self.start.stirrer1.start(float(form["stirrer"]))
                        except :
                            pass
                if "rampUp" in form.keys():
                    print("ramp Up")
                    self.start.pid1.setSetPoint(self.start.t1.getVal())
                    self.start.ctl1.run()

                if "reset" in form.keys():
                    if form["reset"] == "true" :
                       self.start.pid1.setI_err(0)
                if "setI" in form.keys():
                   self.start.pid1.setI_err(float(form["setI"])/self.start.pid1.getK_i())
                if "plotMinutes" in form.keys():
                        regler.plotSeconds
                if "rampup2" in form.keys():
                    # ramp up to value in specified time
                    minutes=float(form["rampup2"]["minutes"])
                    temp=float(form["rampup2"]["temp"])
                    cur_val=self.start.pid1.getSetPoint()
                    print(minutes,temp)
                    if cur_val != temp:
                        if minutes== 0 :
                            self.start.setRamp(0)
                            self.start.setSetPoint(temp)
                            self.start.pid1.setSetPoint(temp)
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
            print("report status")
            power = self.start.pid1.getCtlSig()
            if power > 100:
                power = 100
            elif power < -100:
                power = -100

            data = {
            'time': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),
            'temp': self.start.t1.getVal(),
            'set_point': self.start.pid1.getSetPoint(),
            'k_i': self.start.pid1.getK_i(),
            'k_p': self.start.pid1.getK_p(),
            'plotMinutes' : 0,#regler.plotSeconds/60,
            'actuating_value' : self.start.pid1.getCtlSig(),
            'err' :self.start.pid1.getErr()*self.start.pid1.getK_p(),
            'i_err' : self.start.pid1.getI_err()*self.start.pid1.getK_i(),
            'heater' :self.start.ctl1.heaterIsOn(),
            'cooler' :self.start.ctl1.coolerIsOn(),
            'stirrer' :self.start.stirrer1.isRunning(),
            'power' :power,#regler.power,
            'reg' :self.start.ctl1.isRunning(),
            'ramp' :self.start.getRamp(),
            'target' :self.start.getTarget(),
            'period' :self.start.ctl1.getPeriod(),
            'frozen' :self.start.pid1.getFrozen(),
            'tilt_temp' : self.start.tilt.temp,
            'tilt_grav' : self.start.tilt.grav,
            'ntc1':self.start.ntc1.getVal(),
            'ntc2': self.start.ntc2.getVal()
                }

            try:
                conn = http.client.HTTPSConnection(self.server_address, context=self.sslContext)
                body=urlencode(data,quote_via=quote_plus)
                conn.request("POST", "/brewserver/status/update/",headers={"Content-Type":"application/x-www-form-urlencoded"},body=body)
                r1 = conn.getresponse()
                f=open("response.html","w")
                f.write(r1.read().decode('utf-8'))
                f.close()
            except:
                continue
            # print(r1.status, r1.reason)
            self.lock.acquire()

def escape(s):
    return s


