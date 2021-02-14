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
    const axis = process.argv[2];
    const data1 = process.argv[3];
    const data2 = process.argv[4];

    var barData = {
        datasets: [{
            label: "Africa",
            backgroundColor: "rgba(226,137,85,0.8)",
            data: []
        }],
        labels: []
    };

    if (axis) {
        var index = 0;
        var trimmedParam = axis.replace('[', '').replace(']', '');
        trimmedParam.split(",").forEach(function (item) {
            barData.labels.push(item);
            index++;
        });
    }

    if (data1) {
        var index = 0;
        var trimmedParam = data1.replace('[', '').replace(']', '');
        trimmedParam.split(",").forEach(function (item) {
            barData.datasets[0].data.push(item);
            index++;
        });
        barData.datasets[0].label = 'birth';
    }

    if (data2) {
        second_data = {
            label: "Europe",
            backgroundColor: "rgba(226,184,85,0.8)",
            data: []
        }
        barData.datasets.push(second_data);

        var index = 0;
        var trimmedParam = data2.replace('[', '').replace(']', '');
        trimmedParam.split(",").forEach(function (item) {
            barData.datasets[1].data.push(item);
            index++;
        });
        barData.datasets[1].label = 'death';
    }

    const configuration = {
        type: 'bar',
        data: barData,
        options: {
            legend: {
                display: false
            },
        }
    };

    const image = await chartJSNodeCanvas.renderToBuffer(configuration);
    process.stdout.write(image);
    process.stdout.end();
})();