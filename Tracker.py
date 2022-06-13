import csv
import glob
import copy
import requests
import numpy as np

class Tracker():
    def track(self, id = None, train = False):
        all = requests.get(url="http://localhost:8080/districts").json()
        IterableData = copy.deepcopy(all["data"])
        if id!= None:
            IterableData = []
            IterableData.append(id)
        for i, x in enumerate(IterableData):
            print(x)
            data = requests.get(url=f"http://localhost:8080/districts/{x}/history/incidence").json()
            with open(f'data/{x}-{all["data"][x]["name"]}.csv', 'w', newline='') as csvfile:
                print(all["data"][x]["name"])
                writer = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for day in data["data"][f"{x}"]["history"]:
                    writer.writerow([day["weekIncidence"], day["date"]])
                    import os

        if train:           
            alldata = []

            for u, filepath in enumerate(glob.glob(os.path.join("data", '*.csv'))):
                with open(filepath, 'r') as csvfile:
                    reader = csv.reader(csvfile, skipinitialspace=True)
                    for i, row in enumerate(reader):
                        if row[0]==0 : row[0] = 0.00001
                        alldata.append(float(row[0]))

            min_d = np.min(alldata)
            max_d = np.max(alldata)
            file = open("MinMax.txt","w")
            file.write(str(min_d))
            file.write(",")
            file.write(str(max_d))
            file.close()
            for u, filepath in enumerate(glob.glob(os.path.join("data", '*.csv'))):
                data = []
                with open(filepath, 'r') as csvfile:
                    reader = csv.reader(csvfile, skipinitialspace=True)
                    for i, row in enumerate(reader):
                        data.append(float(row[0]))
                data = (data - min_d) / (max_d - min_d)
                filepath = filepath.split("\\")[-1]
                with open(f'normalized/{filepath}', 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    for i in data:
                        writer.writerow([i])



