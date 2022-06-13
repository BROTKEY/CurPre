from Tracker import Tracker
import torch
import torch.nn as nn
import torch.optim as optim
from Tracker import Tracker
from flask import Flask, render_template
from flask import jsonify
import sys
app = Flask(__name__, static_url_path='/static')
class incidenceGuesser(nn.Module):

    def __init__(self):
        super(incidenceGuesser, self).__init__()
        self.rnn = nn.LSTM(60, 7, 1)
        self.ReLu = nn.ReLU()
        self.hn = torch.rand(1,1,7)
        self.cn = torch.rand(1,1,7)
        

    def forward(self, x):
        x = x.view(-1,1,60)
        output, (hn, cn) = self.rnn(x, (self.hn, self.cn))
        hn = hn.detach()
        cn = cn.detach()
        self.hn = hn
        self.cn = cn
        return self.ReLu(output.view(-1,7))

PATH = './model/model-safed/mk2/cnn.pth'

model = incidenceGuesser()
model.load_state_dict(torch.load(PATH))
model.eval()

def estimate(id, latest = True):
    tracker = Tracker()
    ags = id.split("-")[0]
    tracker.track(id = ags)
    f = open("MinMax.txt", "r")
    MinMax = f.read().split(",")
    f = open(f"data/{id}.csv", "r")
    csv = f.read().split("\n")
    dates = []
    values = []
    MinMax[0] = float(MinMax[0])
    MinMax[1] = float(MinMax[1])
    for x, i in enumerate(csv):
        if i != '':
            dates.append(i.split(",")[1])
            values.append(i.split(",")[0])
    for x, i in enumerate(values):
        if i == '':
            values.pop(x)
        else:
            values[x] = (float(i) - MinMax[0]) / (MinMax[1] - MinMax[0])
    values.reverse()
    latest = values[0:60]
    dates.reverse()
    for x, i in enumerate(dates):
        dates[x] = i.split("T")[0]
    dates = dates[0:60]
    latest.reverse()
    dates.reverse()
    est = model(torch.tensor(latest))
    est = est.tolist()
    print(est, file=sys.stderr)
    latest.extend(est[0]) #remove [0] for non LSTM models readd after deletion
    for x, i in enumerate(latest):
        latest[x] = i * (MinMax[1] - MinMax[0]) + MinMax[0]
    return latest, dates

@app.route('/estimate/latest/<id>', methods = ['GET'])
def EstimateLatest(id = None):
    res = estimate(id)
    return jsonify(res)

@app.route('/track/all', methods = ['POST'])
def trackAlll():
    tracker = Tracker()
    tracker.track()
    return

@app.route("/view/main", methods = ['GET'])
def ViewMain():
    return render_template('main.html')

@app.route('/static/<path:path>')
def send_js(path):
    return app.send_static_file(path)