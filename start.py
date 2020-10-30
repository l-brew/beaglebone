#!/usr/bin/env python3
#from flup.server.fcgi import WSGIServer
from _thread import start_new_thread
import pt100 
from relay_ctrl import relay_ctrl
from pid import pid
import time
from http_comm import http_comm 
import configparser
from dataLogger import dataLogger
from stirrer import stirrer
import threading
import tilt2_client

class start:

    def __init__(self):
        self.cfgName = "temp_reg.config"
        self.dataName = "data.csv"
        self.config = configparser.ConfigParser()
        self.config['Controller']={}
        self.config['Server']={}
        self.config.read(self.cfgName)
        self.ctlConfig=self.config['Controller']
        self.serverConfig=self.config['Server']

        self.logfile =self.dataName
        self.fh=open(self.logfile, "a+")

        self.logger=dataLogger(self.dataName)

        self.stirrer1 = stirrer(self.ctlConfig.get("St1Port","P9_28"))

        self.t1 = pt100.pt100(self.ctlConfig.get("T1Port","P9_40"))

        self.pid1=pid()
        self.pid1.setSetPoint(float(self.ctlConfig.get("SetPoint","20")))
        self.pid1.setK_p(float(self.ctlConfig.get("K_p","6")))
        self.pid1.setK_i(float(self.ctlConfig.get("K_i","0.01")))
        self.pid1.setI_sat_p(float(self.ctlConfig.get("I_sat_p","60")))
        self.pid1.setI_sat_n(float(self.ctlConfig.get("I_sat_n","-60")))

        self.ramp=float(self.ctlConfig.get("Ramp","0"))
        self.setPoint=self.pid1.getSetPoint()


        self.ctl1 = relay_ctrl(self.pid1,self.t1,self.ctlConfig.get("HeaterPort","P8_45"),self.ctlConfig.get("CoolerPort","P8_43"),float(self.ctlConfig.get("CtlPeriod","10")))

        self.tilt = tilt2_client.Tilt2()
        self.tilt.connect()

        self.http1= http_comm(self.pid1,self.ctl1,self.t1,self,self.logger,self.stirrer1,self.tilt)
        self.ctl1.setServer(self.http1)
        self.http1.run()

    def writeConfig(self):
        with open(self.cfgName,"w") as cfgFile:
            self.config.write(cfgFile)
            cfgFile.close()

    def getServer(self):
        return self.http1

    def getRamp(self):
        return self.ramp

    def setRamp(self,ramp):
        self.ramp=ramp

    def getSetPoint(self):
        return self.setPoint

    def setSetPoint(self,setPoint):
        self.setPoint=setPoint

    def getCtlConfig(self):
        return self.ctlConfig

    def getServerConfig(self):
        return self.serverConfig

    def getLogfile(self):
        return self.logfile

    def getTarget(self):
        return self.setPoint

    def mainLoop(self):
        self.ctl1.run()
        ramping=False;
        while True:
            if(self.ramp != 0):
                if(self.pid1.getSetPoint()==self.setPoint):
                    pass
                else:
                    if(abs(self.pid1.getSetPoint() - self.setPoint)) <= (self.ramp/60.):
                        self.pid1.setSetPoint(self.setPoint)
                        self.stirrer1.play([[2000,1],[0,1],[2000,1],[0,1],[2000,1],[0,0]])
                    elif(self.pid1.getSetPoint() < self.setPoint ) :
                        self.pid1.setSetPoint(self.pid1.getSetPoint()+self.ramp/60.)
                    elif(self.pid1.getSetPoint() > self.setPoint ) :
                        self.pid1.setSetPoint(self.pid1.getSetPoint()-self.ramp/60.)
            else:
                self.pid1.setSetPoint(self.setPoint)
                    
            self.t1.update()
            if self.ctl1.isRunning():
                self.pid1.calculate(self.t1.getVal())
            self.http1.update()
            time.sleep(1)
            # self.fh.write("%s;%2.2f;%2.2f;%2.2f;%3.2f\n"%
            self.logger.add([round(time.time(),2),
                        round(self.pid1.getCtlSig(),2),round(self.pid1.getCtlSig(),2),round(self.t1.getVal(),2),round(self.t1.getVal(),2)])


if __name__=="__main__":
    s=start()
    s.mainLoop()
