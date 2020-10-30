import dataLogger

dl = dataLogger.dataLogger("data.csv")
for row in dl.getAll():
    print(row)
