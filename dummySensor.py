class dummySensor:
    def __init__(self):
        self.val=0

    def update(self,cval,ctrlSig):
        self.val=cval+ctrlSig*0.005-0.0001*cval

    def getVal(self):
        return self.val
