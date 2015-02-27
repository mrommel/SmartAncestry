var http = require('http');
var url = require('url');
var Canvas = require('canvas'),
    canvas = new Canvas(600, 450),
    ctx = canvas.getContext('2d'),
    Chart = require('../'),
    data = require('./bar.json'), 
    fs = require('fs');

var server = http.createServer(function(req,res) {
	// parse url
	var request = url.parse(req.url, true);
	console.log("request: '" + request.pathname + "'");
	var query = request.query;

	if (request.pathname == '/bar.png') {
		if (query.data1) {
			var index = 0;
			var trimmedParam = query.data1.replace('[', '').replace(']', '');
			trimmedParam.split(",").forEach(function (item) {
				data.datasets[0].data[index] = item;
				index++;
			});
		}
	
		if (query.data2) {
			var index = 0;
			var trimmedParam = query.data2.replace('[', '').replace(']', '');
			trimmedParam.split(",").forEach(function (item) {
				data.datasets[1].data[index] = item;
				index++;
			});
		}
	
		if (query.axis) {
			var index = 0;
			query.axis.split(",").forEach(function (item) {
				data.labels[index] = item;
				index++;
			});
		}

		ctx.fillStyle = '#fff';
		ctx.fillRect(0, 0, canvas.width, canvas.height);
		var chart = new Chart(ctx).Bar(data);
	
		console.log("deliver bar.png?");
		canvas.toBuffer(function (err, buf) {
			if (err) throw err;
			res.writeHead(200, { 'Content-Type': 'image/png' });
			res.write(buf);
			res.end();
		});
	} else if (request.pathname == '/pie.png') {
	
		var pieData = [
					{
						value: 48,
						color: "rgba(151,187,205,0.5)",
						highlight: "#FF5A5E",
						label: "Item1"
					},
					{
						value: 33,
						color: "rgba(220,220,220,0.5)",
						highlight: "#FF5A5E",
						label: "Item2"
					},	
				];
				
		if (query.data) {
			var index = 0;
			var trimmedParam = query.data.replace('[', '').replace(']', '');
			trimmedParam.split(",").forEach(function (item) {
				//console.log("pie set " + index + " from " + pieData[index].value + " to value = '" + item + "'");
				if (pieData[index] == undefined) {
					pieData[index] = {
						value: 33,
						color: "rgba(220,220,220,0.5)",
						highlight: "#FF5A5E",
						label: "Item2"
					};
				}
				pieData[index].value = Math.round(item);
				index++;
			});
		}
		
		if (query.colors) {
			var index = 0;
			var trimmedParam = query.colors.replace('[', '').replace(']', '');
			//console.log("pie set colors: " + trimmedParam);
			trimmedParam.split(",").forEach(function (item) {
				if (pieData[index] == undefined) {
					pieData[index] = {
						value: 33,
						color: "rgba(220,220,220,0.5)",
						highlight: "#FF5A5E",
						label: "Item2"
					};
				}
				pieData[index].color = '#' + item + '';
				//console.log("pie set " + index + " color = #" + item);
				index++;
			});
		}
		pieData.forEach(function (pieItem) {
			console.log("pie data: value=" + pieItem.value + ", color=" + pieItem.color);
		});
	
		ctx.fillStyle = '#fff';
		ctx.fillRect(0, 0, canvas.width, canvas.height);
		var chart = new Chart(ctx).Pie(pieData);
	
		console.log("deliver pie.png?");
		canvas.toBuffer(function (err, buf) {
			res.writeHead(200, { 'Content-Type': 'image/png' });
			res.write(buf);
			res.end();
		});
	} else {
		res.writeHead(200, {"Content-Type": "text/plain"});
  		res.end("Hello World\n");
	}
});
server.listen(4444);
console.log("Listening at http://localhost:4444")

