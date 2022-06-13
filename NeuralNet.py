import torch
import torch.nn as nn
import torch.optim as optim
import os
import glob
import csv
import matplotlib.pyplot as plt
import copy

epochs = 6
device = torch.device("cpu")
if torch.cuda.is_available():
    device = torch.device("cuda")

def loader(path):
    batches=[]
    for y in range(100):
        for __, filepath in enumerate(glob.glob(os.path.join(path, '*.csv'))):
            with open(filepath, 'r') as csvfile:
                reader = csv.reader(csvfile, skipinitialspace=True)
                data = []
                result = []
                d = []
                r = []
                z = 0 -y
                for _, row in enumerate(reader):
                    if z < 60 and z > -1:
                        d.append(float(row[0]))
                    if z < 67 and z > 59:
                        r.append(float(row[0]))
                    if z == 67:
                        data.append(d)
                        result.append(r)
                        d = []
                        r = []
                        z = 0
                    else: 
                        z += 1
                batches.append((data,result))
    return batches

def get_lr(optimizer):
    for param_group in optimizer.param_groups:
        return param_group['lr']

def train(model, fullLoops, loaderFunc):
    model.train()
    loss = nn.L1Loss().to(device)
    optimizer = optim.Adam(model.parameters(), lr = 0.01)
    lossVis = []
    cache = []
    data = copy.deepcopy(loaderFunc)
    for epoch in range(fullLoops):
        count = 0
        avgLoss = 0
        for i, batches in enumerate(data):
            batch, target = batches
            target = torch.tensor(target).to(device = device)
            batch = torch.tensor(batch).to(device = device)
            pred = model(batch)
            l = loss(pred, target)
            optimizer.zero_grad()
            l.backward()
            optimizer.step()
            cache.append(l.item())
            count += 1
            avgLoss += l
            if i%300 == 0 and i != 0:
                print(f"300 batches done: current avg loss = {avgLoss / count}")
                avgLoss = 0
                count = 0
        print(f'epoch {epoch +1}: avg loss = {avgLoss / count},lr: {round(get_lr(optimizer), 8)}')
        lossVis.extend(cache)
    plt.plot(lossVis)
    plt.show()

def accuracy(predictions, labels):
    return torch.mean((predictions == labels).float())

class incidenceGuesser(nn.Module):

    def __init__(self):
        super(incidenceGuesser, self).__init__()
        numberOfHiddenLayers = 3
        self.rnn = nn.LSTM(60, 14, numberOfHiddenLayers)
        self.ReLu = nn.ReLU()
        self.linear = nn.Linear(14,7)
        self.ReLu = nn.ReLU()
        self.hn = torch.rand(numberOfHiddenLayers,1,14).to(device = device)
        self.cn = torch.rand(numberOfHiddenLayers,1,14).to(device = device)
        

    def forward(self, x):
        x = x.view(-1,1,60)
        output, (hn, cn) = self.rnn(x, (self.hn, self.cn))
        hn = hn.detach()
        cn = cn.detach()
        self.hn = hn
        self.cn = cn
        return self.ReLu(self.linear(self.ReLu(output.view(-1,14))))

model = incidenceGuesser()
PATH = './model/trained/cnn.pth'
model.to(device=device)
model.train()

print(model)

train(model, epochs, loader(path = 'normalized'))
torch.save(model.state_dict(), PATH)
