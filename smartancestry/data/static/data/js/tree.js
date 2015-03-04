var http = require('http');
var url = require('url');
var Canvas = require('canvas'),
    canvas = new Canvas(940, 1160),
    ctx = canvas.getContext('2d'),
    AncestryTree = require('../ancestryTree.js');

var server = http.createServer(function(req,res) {
	// parse url
	var request = url.parse(req.url, true);
	console.log("request: '" + request.pathname + "'");
	var query = request.query;
	
	if (request.pathname == '/tree.png') {
		ctx.fillStyle = '#fcfcfc';
		ctx.fillRect(0, 0, canvas.width, canvas.height);

		var personData = [
				{
					id: 34,
					level: 0,
					selected: 0,
					name: "♂ Arno Karl Hermann Rommel",
					underline: {start: 2, end: 6}, 
					birth: 'Geb.: 11.10.1909 Berlin', 
					death: 'Gest.: 03.04.1986 Berlin',
				},
				{
					id: 37,
					level: 0,
					selected: 0,
					name: "♀ Dorothea Ilse Rommel",
					underline: {start: 11, end: 15}, 
					birth: 'Geb.: 21.02.1916 Beuthen', 
					death: 'Gest.: 11.08.1994 Berlin',
				},
				{
					id: 5,
					level: 1,
					selected: 0,
					name: "♂ Peter Arno Rommel",
					underline: {start: 2, end: 7}, 
					birth: 'Geb.: 07.04.1943 Gotha', 
					death: 'Gest.:  ',
				},
				{
					id: 11,
					level: 1,
					selected: 0,
					name: "♀ Gudrun Rommel",
					underline: {start: -1, end: -1}, 
					birth: 'Geb.: 09.04.1950 Luckau', 
					death: 'Gest.:  ',
				},
				{
					id: 1,
					level: 2,
					selected: 1,
					name: "♂ Michael Rommel",
					underline: {start: -1, end: -1}, 
					birth: 'Geb.: 03.12.1979 Berlin', 
					death: 'Gest.:  ',
				},
				{
					id: 2,
					level: 2,
					selected: 0,
					name: "♀ Ines Rommel",
					underline: {start: -1, end: -1}, 
					birth: 'Geb.: 17.12.1979 Berlin', 
					death: 'Gest.:  ',
				},
				{
					id: 10,
					level: 0,
					selected: 0,
					name: "♂ Werner Kliemank",
					underline: {start: -1, end: -1}, 
					birth: 'Geb.: 02.02.1931 Krietzschwit ...', 
					death: 'Gest.: 08.01.2000 Dresden',
				},
				{
					id: 9,
					level: 0,
					selected: 0,
					name: "♀ Ingeborg Kliemank",
					underline: {start: -1, end: -1}, 
					birth: 'Geb.: 02.01.1933 Berggießhübel', 
					death: 'Gest.:  ',
				},
				{
					id: 12,
					level: 1,
					selected: 0,
					name: "♀ Ingrid Ingeborg Hermann",
					underline: {start: 2, end: 8}, 
					birth: 'Geb.: 03.01.1954 Berggießhübel', 
					death: 'Gest.:  ',
				},
				{
					id: 24,
					level: 0,
					selected: 0,
					name: "♂ Leonhard Hermann",
					underline: {start: -1, end: -1}, 
					birth: 'Geb.: 26.08.1926 ', 
					death: 'Gest.: 30.07.1990 ',
				},
				{
					id: 25,
					level: 0,
					selected: 0,
					name: "♀ Frieda Hermann",
					underline: {start: -1, end: -1}, 
					birth: 'Geb.: 22.11.1929 ', 
					death: 'Gest.:  ',
				},		
				{
					id: 8,
					level: 1,
					selected: 0,
					name: "♂ Reinhold Walter Hermann",
					underline: {start: 11, end: 17}, 
					birth: 'Geb.: 18.08.1952 Müncheberg', 
					death: 'Gest.:  ',
				},
				{
					id: 3,
					level: 3,
					selected: 0,
					name: "♀ Annalena Rommel",
					underline: {start: -1, end: -1}, 
					birth: 'Geb.: 12.05.2004 Berlin', 
					death: 'Gest.:  ',
				},
				{
					id: 4,
					level: 3,
					selected: 0,
					name: "♂ Marcel Rommel",
					underline: {start: -1, end: -1}, 
					birth: 'Geb.: 13.11.2006 Berlin', 
					death: 'Gest.:  ',
				},
		];
		
		// query string: persons=[(4,3,0,"♂ Marcel Rommel",-1,-1,'Geb.: 13.11.2006 Berlin','Gest.:  ');(4,3,0,"♂ Marcel Rommel",-1,-1,'Geb.: 13.11.2006 Berlin','Gest.:  ')]
		if (query.persons) {
			console.log("got persons");
			
			var index = 0;
			var trimmedParam = query.persons.replace('[', '').replace(']', '');
			trimmedParam.split(";").forEach(function (item) {
				// barChartData.datasets[0].data[index] = item;
				// personData
				console.log("person: " + index + " => " + item);
				index++;
			});
		}
		
		var relationsData = [
			new AncestryTree.Relation(34, 5),
			new AncestryTree.Relation(37, 5),
			new AncestryTree.Relation(5, 1),				
			new AncestryTree.Relation(11, 1),				
			new AncestryTree.Relation(2, 3),				
			new AncestryTree.Relation(2, 4),
			new AncestryTree.Relation(10, 12),	
			new AncestryTree.Relation(9, 12),	
			new AncestryTree.Relation(12, 2),		
			new AncestryTree.Relation(24, 8),		
			new AncestryTree.Relation(25, 8),			
			new AncestryTree.Relation(8, 2),			
			new AncestryTree.Relation(1, 3),			
			new AncestryTree.Relation(1, 4),			
		];
		
		// query string: relations=[(1,2);(3,1)]
		if (query.relations) {
			console.log("got relations");
			
			var index = 0;
			var trimmedParam = query.relations.replace('[', '').replace(']', '');
			trimmedParam.split(";").forEach(function (item) {
				// barChartData.datasets[0].data[index] = item;
				// relationsData
				console.log("relation: " + index + " => " + item);
				index++;
			});
		}

		var ancestryTree = new AncestryTree.AncestryTree(ctx, personData, relationsData);
		ancestryTree.draw();
	
		console.log("deliver tree.png");
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

server.listen(4445);
console.log("Listening at http://localhost:4445")