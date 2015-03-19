// ///////////////////////////////////////////
//
// Rectangle
//
// ///////////////////////////////////////////

var Rectangle = function(x, y, width, height) {
	this.x = x;
	this.y = y;
	this.width = width;
	this.height = height;
};

Rectangle.prototype.move = function(dx, dy) {
	this.x += dx;
	this.y += dy;
};

Rectangle.prototype.intersection = function(rect) {
	var x0 = Math.max(this.x, rect.x);
	var y0 = Math.max(this.y, rect.y);
	var x1 = Math.min(this.x + this.width, rect.x + rect.width);
	var y1 = Math.min(this.y + this.height, rect.y + rect.height);
	
	return new Rectangle(x0, y0, Math.max(x1 - x0, 0), Math.max(y1 - y0, 0));
};

Rectangle.prototype.size = function() {
	return this.width * this.height;
};

Rectangle.prototype.expand = function(increment) {

	this.x -= increment;
	this.y -= increment;
	this.width += 2*increment;
	this.height += 2*increment; 

	return this;
};

Rectangle.prototype.toString = function() {
	return 'Rectangle(' + this.x + ', ' + this.y + ', ' +this.width + ', ' + this.height + ')';
};

// ///////////////////////////////////////////
//
// Relation
//
// ///////////////////////////////////////////

function lengthOfPoint(x0, y0, x1, y1) {
	return Math.sqrt((x0-x1) * (x0-x1) + (y0-y1) * (y0-y1));
};

var Relation = function(source, destination) {
	this.source = source;
	this.destination = destination;
};

Relation.prototype.getSourcePerson = function(persons) {
	var person;

	for (index = 0; index < persons.length; ++index) {
		if (persons[index].id == this.source) {
			person = persons[index];
		}
	}
	
	return person;
};

Relation.prototype.getDestinationPerson = function(persons) {
	var person;

	for (index = 0; index < persons.length; ++index) {
		if (persons[index].id == this.destination) {
			person = persons[index];
		}
	}
	
	return person;
};

Relation.prototype.length = function(persons, relations) {
	var sourcePerson = this.getSourcePerson(persons);
	if (sourcePerson == undefined) {
		console.log('Cannot find person with id: ' + this.source);
		return 0;
	}
	var cell1 = sourcePerson.getSource();
	
	var destinationPerson = this.getDestinationPerson(persons);
	if (destinationPerson == undefined) {
		console.log('Cannot find person with id: ' + this.destination);
		return 0;
	}
	var cell2 = destinationPerson.getDestination();
	var x0 = (cell1.x + cell2.x) / 2; 
	return lengthOfPoint(cell1.x, cell1.y, x0-2, cell1.y) + lengthOfPoint(x0-2, cell1.y, x0+2, cell2.y) + lengthOfPoint(x0+2, cell2.y, cell2.x, cell2.y);
};
				
Relation.prototype.draw = function(context, persons) {
	var sourcePerson = this.getSourcePerson(persons);
	if (sourcePerson == undefined) {
		console.log('Cannot find person with id: ' + this.source);
		return;
	}
	var cell1 = sourcePerson.getSource();
	
	var destinationPerson = this.getDestinationPerson(persons);
	if (destinationPerson == undefined) {
		console.log('Cannot find person with id: ' + this.destination);
		return;
	}
	var cell2 = destinationPerson.getDestination();
	var x0 = (cell1.x + cell2.x) / 2; 
	
	context.beginPath();
	context.moveTo(cell1.x, cell1.y);
	context.lineTo(x0-2, cell1.y);
	context.lineTo(x0+2, cell2.y);
	context.lineTo(cell2.x, cell2.y);
	context.strokeStyle = "#000";
	context.stroke();
};

// ///////////////////////////////////////////
//
// Person
//
// ///////////////////////////////////////////

var Person = function(id, name, birth, death) {
	this.id = id;
	this.name = name;
	this.name = this.name.replace('&amp;auml;', 'ä');
	this.name = this.name.replace('&amp;ouml;', 'ö');
	this.name = this.name.replace('&amp;uuml;', 'ü');
	this.birth = birth;
	this.death = death;
	
	this.x = 0;
	this.y = 0;
	this.width = 0;
	this.height = 0;
	this.selected = false;
};

Person.prototype.getDestination = function() {
	return new Cell(this.x, this.y + this.height / 2);
};

Person.prototype.getSource = function() {
	return new Cell(this.x + this.width, this.y + this.height / 2);
};

Person.prototype.getInfo = function() {
	return this.name;
};

Person.prototype.draw = function(context) {
	context.fillStyle = '#EEEEEE';
	context.fillRect(this.x, this.y, this.width, this.height);
	if (this.selected) {
		context.strokeStyle = '#BB2222';
	} else {
		context.strokeStyle = '#000000';
	}
	context.strokeRect(this.x, this.y, this.width, this.height);
	
	context.fillStyle = '#000000';
	context.font = "bold 9px sans-serif";
	context.textBaseline = "top";
	context.fillText(this.name, this.x + 5, this.y + 5);
	
	// underline name if needed
	if (this.underline.start != -1) {
		var offsetText = this.name.substring(0, this.underline.start);
		var subText = this.name.substring(this.underline.start, this.underline.end);
		var textOffset = context.measureText(offsetText).width;
		var textWidth = context.measureText(subText).width;
		context.beginPath();
		context.moveTo(this.x + 5 + textOffset, this.y + 5 + 10);
		context.lineTo(this.x + 5 + textOffset + textWidth, this.y + 5 + 10);
		context.strokeStyle = "#000";
		context.stroke();
	}
	
	context.font = "9px sans-serif";
	context.textBaseline = "top";
	context.fillText(this.birth, this.x + 5, this.y + 18);
	
	context.font = "9px sans-serif";
	context.textBaseline = "top";
	context.fillText(this.death, this.x + 5, this.y + 30);
};

Person.prototype.distances = function(persons) {
	var value = 0;
	var rectangle = this.rectangle().expand(10);
	
	persons.forEach(function(item) {		
		value = value + rectangle.intersection(item.rectangle().expand(10)).size();
	}, this);
	
	// console.log('distances for ' + rectangle + ' = ' + value);
	return value;
};

Person.prototype.evaluate = function(cell, persons, relations) {
	var value = 0;
	// backup position
	var tmp_x = this.x, tmp_y = this.y;
	
	// apply
	this.x = this.x + cell.x, this.y = this.y + cell.y;
	 
	persons.forEach(function(person) {		
		value = value + person.distances(persons);	
	}, this);		
	
	relations.forEach(function(relation) {		
		value = value + relation.length(persons, relations);
	}, this);
	
	// restore position
	this.x = tmp_x, this.y = tmp_y;
	
	return value;
};

Person.prototype.gradient = function(persons, relations) {
	var cellCurrent = new Cell(0, 0);
	var valueCurrent = this.evaluate(cellCurrent, persons, relations);
	
	var cellTop1 = new Cell(0, 1);
	var valueTop1 = this.evaluate(cellTop1, persons, relations);
	if (valueCurrent > valueTop1) {
		cellCurrent = cellTop1;
		valueCurrent = valueTop1;
	}
	
	var cellTop3 = new Cell(0, 3);
	var valueTop3 = this.evaluate(cellTop3, persons, relations);
	if (valueCurrent > valueTop3) {
		cellCurrent = cellTop3;
		valueCurrent = valueTop3;
	}
	
	var cellBottom1 = new Cell(0, -1);
	var valueBottom1 = this.evaluate(cellTop1, persons, relations);
	if (valueCurrent > valueBottom1) {
		cellCurrent = cellBottom1;
		valueCurrent = valueBottom1;
	}
	
	var cellBottom3 = new Cell(0, -3);
	var valueBottom3 = this.evaluate(cellTop3, persons, relations);
	if (valueCurrent > valueBottom3) {
		cellCurrent = cellBottom3;
		valueCurrent = valueBottom3;
	}
	
	return cellCurrent;
};

Person.prototype.toString = function() {
	return '[Person id:' + this.id + ' ,name:' + this.name + ' ,x:' + this.x + ' ,y:' + this.y + ']';
};

Person.prototype.rectangle = function() {
	return new Rectangle(this.x, this.y, this.width, this.height);
};

// ///////////////////////////////////////////
//
// Cell
//
// ///////////////////////////////////////////

var Cell = function(x, y) {
	this.x = x;
	this.y = y;
};

Cell.prototype.getPerson = function(persons) {
	var person;

	for (index = 0; index < persons.length; ++index) {
		if(persons[index].x <= this.x && this.x <= (persons[index].x + personWidth) && persons[index].y <= this.y && this.y <= (persons[index].y + personHeight)) {
			person = persons[index];
		}
	}
	return person;
};

Cell.prototype.getInfo = function() {
	return 'Cell(' + this.x + ', ' + this.y + ')';
};

Cell.prototype.toString = function() {
	return this.getInfo();
};

// ///////////////////////////////////////////
//
// AncestryTree
//
// ///////////////////////////////////////////

var personWidth = 150;
var personHeight = 44;

function AncestryTree(canvasContext, personData, relationData) {
	this.context = canvasContext;

	this.personData = personData;
	this.relationData = relationData;

	this.width = this.context.canvas.width;
	this.height = this.context.canvas.height;
	
	this.persons = [];
	
	// create
	console.log('AncestryTree: create: ' + this.context);
	console.log('AncestryTree: ' + this.width + 'x' + this.height);

	// find out the intend for each level by counting the items
	var itemsInLevel = [0, 0, 0, 0, 0];
	this.personData.forEach(function(entry) {
		itemsInLevel[entry.level]++;
	});
	console.log('itemsInLevel: ' + itemsInLevel);
	
	// create Person objects
	var intend = [0, 0, 0, 0, 0];
	
	this.personData.forEach(function(entry) {		
		var person = new Person(entry.id, entry.name, entry.birth, entry.death);
		
		person.underline = entry.underline;
		person.x = entry.level * (personWidth + 44) + 7;
		person.y = (this.height - itemsInLevel[entry.level] * (personHeight+10)) / 2 + intend[entry.level] * (personHeight+10);
		person.width = personWidth;
		person.height = personHeight;
		person.selected = entry.selected == 1;
		
		intend[entry.level]++;
		
		this.persons.push(person);
	}, this);
	
	return;
};

AncestryTree.prototype.arrange = function() {

	this.persons.forEach(function(person) {
		var gradient = person.gradient(this.persons, this.relationData);
		//console.log("move: " + person + " = " + gradient);
		person.x = person.x + gradient.x;
		person.y = person.y + gradient.y;
		
	}, this);

	return;
};
	
AncestryTree.prototype.draw = function() {
	// render the Persons
	this.persons.forEach(function(person) {
		person.draw(this.context);
	}, this);

	// render the Relations
	this.relationData.forEach(function(relation) {
		relation.draw(this.context, this.persons);
	}, this);
	
	return;
};
	
AncestryTree.prototype.getCursorPosition = function(e) {
	var x;
	var y;
	if (e.pageX != undefined && e.pageY != undefined) {
		x = e.pageX;
		y = e.pageY;
	}
	else {
		x = e.clientX + document.body.scrollLeft +
			document.documentElement.scrollLeft;
		y = e.clientY + document.body.scrollTop +
			document.documentElement.scrollTop;
	}
	x -= this.context.canvas.offsetLeft;
	y -= this.context.canvas.offsetTop;
	
	return new Cell(x, y);
};

// ///////////////////////////////////////////
//
// Module setup
//
// ///////////////////////////////////////////

if (typeof module === 'object' && module.exports) {
	module.exports.AncestryTree = AncestryTree;
	module.exports.Cell = Cell;
	module.exports.Relation = Relation;
	module.exports.Person = Person;
	module.exports.Rectangle = Rectangle;
}