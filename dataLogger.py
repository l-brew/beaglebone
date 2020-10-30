import csv
class dataLogger:
    
    def __init__(self,filename):
        self.filename=filename
        self.fh=open(filename,"r+")
        csvReader = csv.reader(self.fh,delimiter=';')
        self.data=[]
        for row in csvReader:
            self.data.append(row)

        self.csvWriter =csv.writer(self.fh,delimiter=';')

    def getAll(self):
        print("start")
        for row in self.data:
            yield row
        print("end")
        
    def getJson(self):
        json=""
        for i in range(len(self.data)-1):
            json=json+"["+str(self.data[i][0])+","+str(self.data[i][3])+"],\n"
            if i%500 ==0:
                yield json
                json=""
        yield json
        yield "["+str(self.data[-1][0])+","+str(self.data[-1][3])+"]\n"

    def getSize(self):
        return len(self.data)

    def get(self,start):
        for i in range(start,len(self.data)-1,1):
            yield self.data[i]

    def add(self,row):
        if(len(self.data)>1):
            c1=abs(float(row[0])-float(self.data[-1][0]))<600
            c2=abs(float(row[3])-float(self.data[-1][3]))<0.1
            if(c1 and c2):
                return
        self.data.append(row)
        self.csvWriter.writerow(row)
        self.fh.flush()


