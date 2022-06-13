const axios = require('axios').default;

function estimate(id) {
    if(id == "") {return;}
    axios.get("/estimate/latest/" + id).then((data) => {
        data = data.data
        let last = data[1][59]
        let graph = [];
        for (let x = 0; x < 67; x++) {
            let latest;
            if (x < 60) {
                data[1][x] = new Date(data[1][x])
                latest = data[1][x]
            } else {
                console.log(data);
                data[1][x] = new Date(data[1][x - 1].getTime() + 86400000)
            }
            graph.push([data[1][x], data[0][x]])
        }
        google.charts.load('current', { packages: ['corechart', 'line'] });
        google.charts.setOnLoadCallback(drawBackgroundColor);

        function drawBackgroundColor() {
            var data = new google.visualization.DataTable();
            data.addColumn('date', 'Datum');
            data.addColumn('number', 'Inzidenz');
            data.addRows(graph);

            var dataView = new google.visualization.DataView(data);
            dataView.setColumns([
                0, 1,
                {
                    calc: function (data, row) {

                        if (data.getValue(row, 0).getTime() > new Date(last).getTime()) {
                            return 'red';
                        }
                        return 'blue'
                    },
                    type: 'string',
                    role: 'style'
                }
            ]);

            var options = {
                curveType: 'linear',
                height: 500,
                hAxis: {
                    title: 'Datum'
                },
                vAxis: {
                    title: 'Inzidenz'
                },
                backgroundColor: '#ffffff',
                trendlines: {
                    0: { type: 'linear', color: '#333', opacity: 0.8 },
                },
            };

            var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
            chart.draw(dataView, options);
        }
    })
}

let btn = document.getElementById("update")
btn.addEventListener('click', function(e) {console.log("bing");estimate(document.getElementById("AGS").value)})