var http = require('http');
var url = require('url');
var fs = require('fs');
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
		];
		
		// query string: persons=[(4,3,0,"♂ Marcel Rommel",-1,-1,'Geb.: 13.11.2006 Berlin','Gest.:  ');(4,3,0,"♂ Marcel Rommel",-1,-1,'Geb.: 13.11.2006 Berlin','Gest.:  ')]
		if (query.persons) {
			console.log("got persons");
			
			var index = 0;
			var trimmedParam = query.persons.replace('[', '');
			trimmedParam = trimmedParam.replace(']', '');
			trimmedParam.split(";").forEach(function (item) {
				item = item.replace('{', '');
				item = item.replace('}', '');
				var parts = item.split(",");
				//console.log("person: " + index + " => id:" + parts[0] + ' name:' + parts[3]);
				var personObj = {};
				personObj.id = parts[0];
				personObj.level = parts[1];
				personObj.selected = parts[2];
				personObj.name = parts[3];
				personObj.name = personObj.name.replace('\'', '');
				personObj.name = personObj.name.replace('/xe2/x99/x82', '♂');
				personObj.name = personObj.name.replace('/xe2/x99/x80', '♀');
				personObj.name = personObj.name.replace('Ã¤', 'ä');
				personObj.name = personObj.name.replace('Ã¶', 'ö');
				personObj.name = personObj.name.replace('\'', '');
				console.log('name: ' + personObj.name);
				var underlineObj = { };
				underlineObj.start = parts[4];
				underlineObj.end = parts[5];
				personObj.underline = underlineObj;
				personObj.birth = parts[6];
				console.log('birth: ' + personObj.birth);
				personObj.birth = personObj.birth.replace('/xc3/x9f', 'ß');
				personObj.birth = personObj.birth.replace('/xc3/xbc', 'ü');
				personObj.birth = personObj.birth.replace('/xc3/xa4', 'ä');
				console.log('birth: ' + personObj.birth);
				personObj.death = parts[7];
				console.log('death: ' + personObj.death);
				personObj.death = personObj.death.replace('/xc3/x9f', 'ß');
				personObj.death = personObj.death.replace('/xc3/xbc', 'ü');
				personObj.death = personObj.death.replace('/xc3/xa4', 'ä');
				console.log('death: ' + personObj.death);
				personData.push(personObj);
				//console.log("person: " + index + " => " + item);
				index++;
			});
		}
		
		var relationsData = [		
		];
		
		// query string: relations=[(1,2);(3,1)]
		if (query.relations) {
			console.log("got relations");
			
			var index = 0;
			var trimmedParam = query.relations.replace('[', '').replace(']', '');
			trimmedParam.split(";").forEach(function (item) {
				item = item.replace('(', '');
				item = item.replace(')', '');
				var parts = item.split(",");
				relationsData.push(new AncestryTree.Relation(parts[0], parts[1]));
				//console.log("relation: " + index + " => " + parts[0] + ', ' + parts[1]);
				index++;
			});
		}

		var ancestryTree = new AncestryTree.AncestryTree(ctx, personData, relationsData);
		
		for (var i = 0; i < 20000; i++) {
			ancestryTree.arrange();
		}
		ancestryTree.draw();
	
		console.log("deliver tree.png");
		canvas.toBuffer(function (err, buf) {
			res.writeHead(200, { 'Content-Type': 'image/png' });
			res.write(buf);
			res.end();
		});
	} else if (request.pathname == '/test.html') {
		var testBuffer = 'tests\n\n';
	
		// ///////////////////////
		// test Rectangle intersection1
		var rect1 = new AncestryTree.Rectangle(0, 0, 5, 5);
		var rect2 = new AncestryTree.Rectangle(3, 3, 5, 5);
		var rectErg = rect1.intersection(rect2);
		testBuffer += '# test intersection1:\n';
		testBuffer += 'rect1: ' + rect1 + '\n';
		testBuffer += 'rect2: ' + rect2 + '\n';
		testBuffer += 'rect1.intersection(rect2): ' + rectErg + '\n\n';
		
		// test Rectangle intersection2
		var rect1 = new AncestryTree.Rectangle(2, 0, 2, 5);
		var rect2 = new AncestryTree.Rectangle(3, 3, 5, 5);
		var rectErg = rect1.intersection(rect2);
		testBuffer += '# test intersection2:\n';
		testBuffer += 'rect1: ' + rect1 + '\n';
		testBuffer += 'rect2: ' + rect2 + '\n';
		testBuffer += 'rect1.intersection(rect2): ' + rectErg + '\n\n';
		
		// test Rectangle intersection3
		var rect1 = new AncestryTree.Rectangle(0, 0, 2, 2);
		var rect2 = new AncestryTree.Rectangle(3, 3, 5, 5);
		var rectErg = rect1.intersection(rect2);
		testBuffer += '# test intersection3 (no intersection):\n';
		testBuffer += 'rect1: ' + rect1 + '\n';
		testBuffer += 'rect2: ' + rect2 + '\n';
		testBuffer += 'rect1.intersection(rect2): ' + rectErg + '\n\n';
		
		// ///////////////////////
		// test Rectangle size1
		var rect1 = new AncestryTree.Rectangle(2, 0, 2, 5);
		testBuffer += '# test size1:\n';
		testBuffer += 'rect1: ' + rect1 + '\n';
		testBuffer += 'rect1.size(): ' + rect1.size() + '\n\n';
		
		// test Rectangle size2
		var rect1 = new AncestryTree.Rectangle(2, 0, 0, 0);
		testBuffer += '# test size2:\n';
		testBuffer += 'rect1: ' + rect1 + '\n';
		testBuffer += 'rect1.size(): ' + rect1.size() + '\n\n';
		
		// ///////////////////////
		// test Rectangle expand1
		var rect1 = new AncestryTree.Rectangle(0, 0, 2, 5);
		testBuffer += '# test expand1:\n';
		testBuffer += 'rect1: ' + rect1 + '\n';
		testBuffer += 'rect1.expand(5): ' + rect1.expand(5) + '\n\n';
		
		// test Rectangle expand2
		var rect1 = new AncestryTree.Rectangle(3, 3, 12, 5);
		testBuffer += '# test expand2:\n';
		testBuffer += 'rect1: ' + rect1 + '\n';
		testBuffer += 'rect1.expand(1): ' + rect1.expand(1) + '\n\n';
	
		res.writeHead(200, {"Content-Type": "text/plain"});
  		res.end(testBuffer + '\n');
	} else if (request.pathname == '/favicon.ico') {
		var favicon = fs.readFileSync('../syncly.ico');
		res.writeHead(200, {'Content-Type': 'image/x-icon'} );
		res.end(favicon);
	} else {
		res.writeHead(200, {"Content-Type": "text/plain"});
  		res.end("Hello World\n");
	}
});

server.listen(4445);
console.log("Listening at http://localhost:4445")