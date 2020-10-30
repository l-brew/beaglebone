class pid:
    def __init__(self,err=0.0,i_err=0.0,k_p=100.,k_i=0.001,i_sat_p=60,i_sat_n=-60,setPoint=20.):
        self.err=err
        self.i_err=i_err
        self.k_p = k_p
        self.k_i = k_i
        self.i_sat_p = i_sat_p
        self.i_sat_n = i_sat_n
        self.setPoint= setPoint
        self.ctlSig=0.
        self.frozen=False

    def calculate(self,actVal):
        if self.frozen:
            self.ctlSig=self.setPoint
            return self.ctlSig
        # calculate error
        self.err=self.setPoint-actVal;
        # integrate
        self.i_err = self.i_err + self.err
        # saturate integrator
        if self.i_err * self.k_i > self.i_sat_p :
            self.i_err = self.i_sat_p/self.k_i
        elif self.i_err * self.k_i< self.i_sat_n :
            self.i_err = -self.i_sat_n / self.k_i

        self.ctlSig=self.err*self.k_p + self.i_err * self.k_i
        return self.ctlSig

    def setSetPoint(self,setPoint):
        self.setPoint=setPoint

    def getSetPoint(self):
        return self.setPoint

    def getErr(self):
        return self.err

    def setErr(self,err):
        self.err=err

    def getI_err(self):
        return self.i_err

    def setI_err(self,i_err):
        self.i_err=i_err

    def getK_p (self):
        return self.k_p 

    def setK_p (self,k_p ):
        self.k_p =k_p 

    def getK_i (self):
        return self.k_i 

    def setK_i (self,k_i ):
        self.k_i =k_i 

    def getI_sat_p (self):
        return self.i_sat_p

    def setI_sat_p (self,i_sat_p ):
        self.i_sat_p =i_sat_p

    def getI_sat_n (self):
        return self.i_sat_n 

    def setI_sat_n (self,i_sat_n ):
        self.i_sat_n =i_sat_n 

    def getSetPoint(self):
        return self.setPoint

    def getCtlSig(self):
        return self.ctlSig

    def setCtlSig(self,ctlSig):
        self.ctlSig=ctlSig

    def freeze(self):
        self.frozen=True

    def unfreeze(self):
        self.frozen=False

    def getFrozen(self):
        return self.frozen
