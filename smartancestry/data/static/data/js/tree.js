var http = require('http');
var url = require('url');
var fs = require('fs');
var Canvas = require('canvas'),
    canvas = new Canvas(940, 1160),
    ctx = canvas.getContext('2d'),
    AncestryTree = require('../ancestryTree.js');

/**
 * creates webserver at 4445
 */
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
		
		for (var i = 0; i < 2000; i++) {
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
	
		var detailed = false;
		
		if (query.detailed) {
			detailed = true;
		}
	
		// ///////////////////////
		// test Rectangle intersection1
		var rect1 = new AncestryTree.Rectangle(0, 0, 5, 5);
		var rect2 = new AncestryTree.Rectangle(3, 3, 5, 5);
		var rectErg = rect1.intersection(rect2);
		var passed = rectErg.equals(new AncestryTree.Rectangle(3, 3, 2, 2));
		testBuffer += '# test intersection1: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'rect1: ' + rect1 + '\n';
			testBuffer += 'rect2: ' + rect2 + '\n';
			testBuffer += 'rect1.intersection(rect2): ' + rectErg + '\n\n';
		}
		
		// test Rectangle intersection2
		var rect1 = new AncestryTree.Rectangle(2, 0, 2, 5);
		var rect2 = new AncestryTree.Rectangle(3, 3, 5, 5);
		var rectErg = rect1.intersection(rect2);
		var passed = rectErg.equals(new AncestryTree.Rectangle(3, 3, 1, 2));
		testBuffer += '# test intersection2: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'rect1: ' + rect1 + '\n';
			testBuffer += 'rect2: ' + rect2 + '\n';
			testBuffer += 'rect1.intersection(rect2): ' + rectErg + '\n\n';
		}
		
		// test Rectangle intersection3
		var rect1 = new AncestryTree.Rectangle(0, 0, 2, 2);
		var rect2 = new AncestryTree.Rectangle(3, 3, 5, 5);
		var rectErg = rect1.intersection(rect2);
		var passed = rectErg.equals(new AncestryTree.Rectangle(3, 3, 0, 0));
		testBuffer += '# test intersection3: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'rect1: ' + rect1 + '\n';
			testBuffer += 'rect2: ' + rect2 + '\n';
			testBuffer += 'rect1.intersection(rect2): ' + rectErg + '\n\n';
		}
		
		// ///////////////////////
		// test Rectangle empty1
		var rect1 = new AncestryTree.Rectangle(2, 0, 2, 5);
		var passed = !rect1.empty();
		testBuffer += '# test empty1: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'rect1: ' + rect1 + '\n';
			testBuffer += 'rect1.empty(): ' + rect1.empty() + '\n\n';
		}
		
		// test Rectangle empty2
		var rect1 = new AncestryTree.Rectangle(2, 0, 0, 0);
		var passed = rect1.empty();
		testBuffer += '# test empty2: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'rect1: ' + rect1 + '\n';
			testBuffer += 'rect1.empty(): ' + rect1.empty() + '\n\n';
		}
		
		// ///////////////////////
		// test Rectangle size1
		var rect1 = new AncestryTree.Rectangle(2, 0, 2, 5);
		var passed = rect1.size() == 10;
		testBuffer += '# test size1: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'rect1: ' + rect1 + '\n';
			testBuffer += 'rect1.size(): ' + rect1.size() + '\n\n';
		}
		
		// test Rectangle size2
		var rect1 = new AncestryTree.Rectangle(2, 0, 0, 0);
		var passed = rect1.size() == 0;
		testBuffer += '# test size2: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'rect1: ' + rect1 + '\n';
			testBuffer += 'rect1.size(): ' + rect1.size() + '\n\n';
		}
		
		// ///////////////////////
		// test Rectangle expand1
		var rect1 = new AncestryTree.Rectangle(0, 0, 2, 5);
		var rectErg = rect1.expand(5);
		var passed = rectErg.equals(new AncestryTree.Rectangle(-5, -5, 12, 15));
		testBuffer += '# test expand1: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'rect1: ' + rect1 + '\n';
			testBuffer += 'rect1.expand(5): ' + rectErg + '\n\n';
		}
		
		// test Rectangle expand2
		var rect1 = new AncestryTree.Rectangle(3, 3, 12, 5);
		var rectErg = rect1.expand(1);
		var passed = rectErg.equals(new AncestryTree.Rectangle(2, 2, 14, 7));
		testBuffer += '# test expand2: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'rect1: ' + rect1 + '\n';
			testBuffer += 'rect1.expand(1): ' + rect1.expand(1) + '\n\n';
		}
		
		// ///////////////////////
		// test Rectangle equals1
		var rect1 = new AncestryTree.Rectangle(0, 0, 2, 5);
		var rect2 = new AncestryTree.Rectangle(0, 0, 2, 5);
		var passed = rect1.equals(rect2);
		testBuffer += '# test equals1: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'rect1: ' + rect1 + '\n';
			testBuffer += 'rect2: ' + rect2 + '\n';
			testBuffer += 'rect1.equals(rect2): ' + rect1.equals(rect2) + '\n\n';
		}	
		
		// test Rectangle equals2
		var rect1 = new AncestryTree.Rectangle(0, 0, 2, 5);
		var rect2 = new AncestryTree.Rectangle(0, 3, 2, 5);
		var passed = !rect1.equals(rect2);
		testBuffer += '# test equals2: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'rect1: ' + rect1 + '\n';
			testBuffer += 'rect2: ' + rect2 + '\n';
			testBuffer += 'rect1.equals(rect2): ' + rect1.equals(rect2) + '\n\n';
		}
		
		// test Rectangle equals2
		var rect1 = new AncestryTree.Rectangle(0, 0, 2, 5);
		var rect2 = new AncestryTree.Rectangle(0, 0, 1, 5);
		var passed = !rect1.equals(rect2);
		testBuffer += '# test equals3: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'rect1: ' + rect1 + '\n';
			testBuffer += 'rect2: ' + rect2 + '\n';
			testBuffer += 'rect1.equals(rect2): ' + rect1.equals(rect2) + '\n\n';
		}
		
		// test Rectangle move1
		var rect1 = new AncestryTree.Rectangle(0, 0, 2, 5);
		var rectErg = rect1.move(1, 1);
		var passed = rectErg.equals(new AncestryTree.Rectangle(1, 1, 2, 5));
		testBuffer += '# test move1: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'rect1: ' + rect1 + '\n';
			testBuffer += 'rect1.move(1, 1): ' + rectErg + '\n';
		}
		
		testBuffer += '\n\nPerson:\n';
		
		// ////////////////////////////
		// test Person constructor
		var person1 = new AncestryTree.Person(0, 'name', 'birth', 'death');
		var passed = person1.id == 0;
		testBuffer += '# test Person.id: ' + passed + '\n';
		var passed = person1.name == 'name';
		testBuffer += '# test Person.name: ' + passed + '\n';
		var passed = person1.birth == 'birth';
		testBuffer += '# test Person.birth: ' + passed + '\n';
		var passed = person1.death == 'death';
		testBuffer += '# test Person.death: ' + passed + '\n';
		if (detailed) {
			testBuffer += '\n';
		}
		
		// test Person.getDestination1
		var person1 = new AncestryTree.Person(0, 'name', 'birth', 'death');
		person1.x = 10, person1.y = 10, person1.width = 50, person1.height = 50;
		var pointDest = person1.getDestination();
		var passed = pointDest.x == 10 && pointDest.y == 35;
		testBuffer += '# test getDestination1: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'person1: ' + person1 + '\n';
			testBuffer += 'person1.getDestination(): ' + pointDest + '\n\n';
		}
		
		// test Person.getSource1
		var person1 = new AncestryTree.Person(0, 'name', 'birth', 'death');
		person1.x = 10, person1.y = 10, person1.width = 50, person1.height = 50;
		var pointDest = person1.getSource();
		var passed = pointDest.x == 60 && pointDest.y == 35;
		testBuffer += '# test getSource1: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'person1: ' + person1 + '\n';
			testBuffer += 'person1.getSource(): ' + pointDest + '\n\n';
		}
		
		// test Person.distances1
		var person1 = new AncestryTree.Person(0, 'name', 'birth', 'death');
		person1.x = 10, person1.y = 10, person1.width = 50, person1.height = 50;
		var person2 = new AncestryTree.Person(1, 'name1', 'birth1', 'death1');
		person2.x = 10, person2.y = 60, person2.width = 50, person2.height = 50;
		var persons = [ person1, person2 ];
		var result = person1.distances(persons);
		var passed = result == 1400;
		testBuffer += '# test distances1: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'person1: ' + person1 + '\n';
			testBuffer += 'person2: ' + person2 + '\n';
			testBuffer += 'person1.distances(persons): ' + result + '\n\n';
		}
		
		// test Person.evaluate1
		var person1 = new AncestryTree.Person(0, 'name', 'birth', 'death');
		person1.x = 10, person1.y = 10, person1.width = 50, person1.height = 50;
		var person2 = new AncestryTree.Person(1, 'name1', 'birth1', 'death1');
		person2.x = 10, person2.y = 60, person2.width = 50, person2.height = 50;
		var persons = [ person1, person2 ];
		var relation = new AncestryTree.Relation(0, 1);
		var result = Math.round(person1.evaluate(new AncestryTree.Point(10, 10), persons, [relation]));
		var passed = result == 1402;
		testBuffer += '# test evaluate1: ' + passed + '\n';
		if (detailed) {
			testBuffer += 'person1: ' + person1 + '\n';
			testBuffer += 'person2: ' + person2 + '\n';
			testBuffer += 'relation: ' + relation + '\n';
			testBuffer += 'person1.evaluate(new Point(10, 10), persons, [relation]): ' + result + '\n\n';
		}
	
		res.writeHead(200, {"Content-Type": "text/plain"});
  		res.end(testBuffer + '\n');
	} else if (request.pathname == '/favicon.ico') {
		var favicon = fs.readFileSync('../../../images/favicon.ico');
		res.writeHead(200, {'Content-Type': 'image/x-icon'} );
		res.end(favicon);
	} else {
		res.writeHead(200, {"Content-Type": "text/plain"});
  		res.end("Hello World\n");
	}
});

server.listen(4445);
console.log("Listening at http://localhost:4445")