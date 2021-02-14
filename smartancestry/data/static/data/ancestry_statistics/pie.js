const { ChartJSNodeCanvas } = require('chartjs-node-canvas');
var Chart = require('chart.js');

const width = 800;
const height = 600;

const chartCallback = (ChartJS) => {

    // Global config example: https://www.chartjs.org/docs/latest/configuration/
    ChartJS.defaults.global.elements.rectangle.borderWidth = 2;
    ChartJS.defaults.global.defaultFontFamily = "'Euphemia UCAS', 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";
	ChartJS.defaults.global.defaultFontSize = 20;
	ChartJS.defaults.global.defaultFontColor = "#333";

    // Global plugin example: https://www.chartjs.org/docs/latest/developers/plugins.html
    ChartJS.plugins.register({
        // plugin implementation
        beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
        }
    });
    // New chart type example: https://www.chartjs.org/docs/latest/developers/charts.html
    ChartJS.controllers.MyType = ChartJS.DatasetController.extend({
        // chart implementation
    });
};
const chartJSNodeCanvas = new ChartJSNodeCanvas({ width, height, chartCallback });

(async () => {
    const data = process.argv[2];
    const colors = ["#e28955", "#e2b855", "#dde255", "#aee255", "#7fe255", "#55e25a", "#55e289", "#55e2b8", "#55dde2", "#55aee2",
    "#557fe2", "#e25a55", "#e28955", "#e2b855", "#dde255", "#aee255", "#7fe255", "#55e25a", "#55e289", "#55e2b8"];

    var pieData = {
        datasets: [{
            backgroundColor: [
                "rgba(226,137,85,0.8)",
                "rgba(226,184,85,0.8)"
            ],
            data: [10, 20]
        }],
        labels: [
            'Red',
            'Blue'
        ]
    };

    if (data) {
        var index = 0;
        var trimmedParam = data.replace('[', '').replace(']', '');
        trimmedParam.split(",").forEach(function (item) {
            if (pieData.datasets[0].backgroundColor[index] == undefined) {
                pieData.datasets[0].backgroundColor[index] = "rgba(220,220,220,0.5)";
                pieData.datasets[0].data[index] = 33;
                pieData.labels[index] = "Item2";
            }
            pieData.datasets[0].backgroundColor[index] = colors[index];
            pieData.datasets[0].data[index] = Math.round(item);
            pieData.labels[index] = '' + Math.round(item);
            index++;
        });
    }

    const configuration = {
        type: 'pie',
        data: pieData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                display: false
            },
            plugins: {
                labels: {
                    render: 'label',
                    fontColor: '#333',
                }
            }
        }
    };
    const image = await chartJSNodeCanvas.renderToBuffer(configuration);
    process.stdout.write(image);
    process.stdout.end();
})();