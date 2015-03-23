// ///////////////////////////////////////////
//
// Rectangle
//
// ///////////////////////////////////////////

/**
 * Represents a Rectangle.
 *
 * @constructor
 * @param {int} x - The x-coordinate of the Rectangle.
 * @param {int} y - The y-coordinate of the Rectangle.
 * @param {int} width - The width of the Rectangle.
 * @param {int} height - The height of the Rectangle.
 */
var Rectangle = function(x, y, width, height) {
	this.x = x;
	this.y = y;
	this.width = width;
	this.height = height;
};

/**
 * move the Rectangle
 *
 * @param {int} dx - The delta of x-coordinate of the Rectangle.
 * @param {int} dy - The delta of y-coordinate of the Rectangle.
 * @return current Rectanlge
 */
Rectangle.prototype.move = function(dx, dy) {
	this.x += dx;
	this.y += dy;
	
	return this;
};

/**
 * returns the intersection of current Rectangle with another Rectangle
 *
 * @param {Rectangle} rect - The Rectangle to get the intersection with the Rectangle.
 * @return intersection of current Rectangle and rect
 */
Rectangle.prototype.intersection = function(rect) {
	var x0 = Math.max(this.x, rect.x);
	var y0 = Math.max(this.y, rect.y);
	var x1 = Math.min(this.x + this.width, rect.x + rect.width);
	var y1 = Math.min(this.y + this.height, rect.y + rect.height);
	
	return new Rectangle(x0, y0, Math.max(x1 - x0, 0), Math.max(y1 - y0, 0));
};

/**
 * returns true if the current Rectangle has size equal to zero
 *
 * @see size()
 * @return true if the current Rectangle has size equal to zero
 */
Rectangle.prototype.empty = function() {
	return this.size() == 0;
};

/**
 * returns the size of current Rectangle
 *
 * @return size of current Rectangle
 */
Rectangle.prototype.size = function() {
	return this.width * this.height;
};

/**
 * returns the expansion of the current Rectangle
 *
 * @param {int} increment - The increment value for the Rectangle.
 * @return current Rectangle
 */
Rectangle.prototype.expand = function(increment) {

	this.x -= increment;
	this.y -= increment;
	this.width += 2*increment;
	this.height += 2*increment; 

	return this;
};

/**
 * returns true if other is equal to the current Rectangle
 *
 * @param {Rectangle} other - The other Rectangle to compare with.
 * @return true if other is equal to the current Rectangle
 */
Rectangle.prototype.equals = function(other) {

	return this.x == other.x && this.y == other.y && this.width == other.width && this.height == this.height;
};

/**
 * returns the string of current Rectangle
 *
 * @return string of current Rectangle
 */
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

/**
 * Represents a Relation between Persons.
 *
 * @constructor
 * @param {int} source - The Persons source id of the Relation.
 * @param {int} destination - The Persons destination id of the Relation.
 */
var Relation = function(source, destination) {
	this.source = source;
	this.destination = destination;
};

/**
 * returns the source Person of current Relation
 *
 * @return source {Person} of current Relation
 */
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
				
/**
 * draws the Relation on the Context
 *
 * @param {Context} context to draw on
 * @return true if the relation could be drawn, false otherwise
 */
Relation.prototype.draw = function(context, persons) {
	if (context == undefined) {
		return;
	}
	var sourcePerson = this.getSourcePerson(persons);
	if (sourcePerson == undefined) {
		console.log('Cannot find person with id: ' + this.source);
		return false;
	}
	var cell1 = sourcePerson.getSource();
	
	var destinationPerson = this.getDestinationPerson(persons);
	if (destinationPerson == undefined) {
		console.log('Cannot find person with id: ' + this.destination);
		return false;
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
	
	return true;
};

// ///////////////////////////////////////////
//
// Person
//
// ///////////////////////////////////////////

/**
 * Represents a Person.
 *
 * @constructor
 * @param {int} id - The identifier of the Person.
 * @param {string} name - The name of the Person.
 * @param {string} birth - The birth string of the Person.
 * @param {string} death - The death string of the Person.
 */
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

/**
 * get end point of {Relation} of this {Person} 
 *
 * @return {Point} end point
 */
Person.prototype.getDestination = function() {
	return new Point(this.x, this.y + this.height / 2);
};

/**
 * get start point of {Relation} of this {Person}
 *
 * @return {Point} start point
 */
Person.prototype.getSource = function() {
	return new Point(this.x + this.width, this.y + this.height / 2);
};

Person.prototype.getInfo = function() {
	return this.name;
};

/**
 * draws the {Person} on the {Context}
 *
 * @param {Context} context to draw on
 */
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

/**
 * get distances of current {Person} to persons
 *
 * @param {Person} persons - Array of {Person} to get the distances to this {Person}
 * @return overlapping area of persons
 */
Person.prototype.distances = function(persons) {
	var value = 0;
	var rectangle = this.rectangle().expand(10);
	
	persons.forEach(function(item) {		
		if (item.id != this.id) {
			value = value + rectangle.intersection(item.rectangle().expand(10)).size();
		}
	}, this);
	
	// console.log('distances for ' + rectangle + ' = ' + value);
	return value;
};

/**
 * get distances of current {Person} to persons
 *
 * @see Person.distances(persons)
 * @param {Point} cell - tmp changed position of the current Person
 * @param {Person} persons - Array of {Person} to get the distances to this {Person}
 * @param {Relation} relations - Array of {Relation} of all relations
 */
Person.prototype.evaluate = function(cell, persons, relations) {
	var value = 0;
	// backup position
	var tmp_x = this.x, tmp_y = this.y;
	
	// apply changed position
	this.x = this.x + cell.x, this.y = this.y + cell.y;
	 
	// calculate overlapping to all other persons
	persons.forEach(function(person) {		
		value = value + person.distances(persons) / 10;	
	}, this);		
	
	// sum of all relation length 
	relations.forEach(function(relation) {		
		value = value + relation.length(persons, relations) * 10;
	}, this);
	
	// restore position
	this.x = tmp_x, this.y = tmp_y;
	
	return value;
};

/**
 * determines if the Person should be moved up or down
 *
 * @return gradient the Person should be moved up or down
 */
Person.prototype.gradient = function(persons, relations) {
	var cellCurrent = new Point(0, 0);
	var valueCurrent = this.evaluate(cellCurrent, persons, relations);
	
	var cellTop1 = new Point(0, 1);
	var valueTop1 = this.evaluate(cellTop1, persons, relations);
	if (valueCurrent > valueTop1) {
		cellCurrent = cellTop1;
		valueCurrent = valueTop1;
	}
	
	var cellTop3 = new Point(0, 3);
	var valueTop3 = this.evaluate(cellTop3, persons, relations);
	if (valueCurrent > valueTop3) {
		cellCurrent = cellTop3;
		valueCurrent = valueTop3;
	}
	
	var cellBottom1 = new Point(0, -1);
	var valueBottom1 = this.evaluate(cellBottom1, persons, relations);
	if (valueCurrent > valueBottom1) {
		cellCurrent = cellBottom1;
		valueCurrent = valueBottom1;
	}
	
	var cellBottom3 = new Point(0, -3);
	var valueBottom3 = this.evaluate(cellBottom3, persons, relations);
	if (valueCurrent > valueBottom3) {
		cellCurrent = cellBottom3;
		valueCurrent = valueBottom3;
	}
	
	return { 'point': cellCurrent, 'value': valueCurrent};
};

/**
 * string representation of the Person
 *
 * @return string representation of the Person
 */
Person.prototype.toString = function() {
	return '[Person id:' + this.id + ' ,name:' + this.name + ' ,x:' + this.x + ' ,y:' + this.y + ']';
};

/**
 * get the bounding rectangle of the Person
 *
 * @return {Rectangle} of the Person
 */
Person.prototype.rectangle = function() {
	return new Rectangle(this.x, this.y, this.width, this.height);
};

// ///////////////////////////////////////////
//
// Point
//
// ///////////////////////////////////////////

/**
 * Represents a Point.
 *
 * @constructor
 * @param {int} x - The x-coordinate of the Point.
 * @param {int} y - The y-coordinate of the Point.
 */
var Point = function(x, y) {
	this.x = x;
	this.y = y;
};

/**
 * get Person at current point of which hits a person in the list
 *
 * @param {Person} persons - Array of {Person} to find the 
 * @return {Person} at the current Points location
 */
Point.prototype.getPerson = function(persons) {
	var person;

	for (index = 0; index < persons.length; ++index) {
		if(persons[index].x <= this.x && this.x <= (persons[index].x + personWidth) && persons[index].y <= this.y && this.y <= (persons[index].y + personHeight)) {
			person = persons[index];
		}
	}
	return person;
};

/**
 * get the string representation of the current Point
 *
 * @return string representation of the current Point
 */
Point.prototype.toString = function() {
	return 'Point(' + this.x + ', ' + this.y + ')';
};

// ///////////////////////////////////////////
//
// AncestryTree
//
// ///////////////////////////////////////////

var personWidth = 150;
var personHeight = 44;

/**
 * Represents an AncestryTree.
 *
 * @constructor
 * @param {Context} canvasContext - The canvasContext of the AncestryTree.
 * @param {Array<Person>} personData - The Array of Persons of the AncestryTree.
 * @param {Array<Relation>} relationData - The Array of Relations of the AncestryTree.
 */
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

/**
 * arranges the persons on the AncestryTree
 */
AncestryTree.prototype.arrange = function() {

	var bestIndex = 0;
	var bestGradient = { 'point': new Point(0, 0), 'value': 1000000 };

	var index = 0;
	this.persons.forEach(function(person) {
		var gradient = person.gradient(this.persons, this.relationData);
		if (bestGradient.value > gradient.value) {
			bestGradient = gradient;
			bestIndex = index;
		}
		
		index = index + 1;
	}, this);
	
	this.persons[bestIndex].x = this.persons[bestIndex].x + bestGradient.point.x;
	this.persons[bestIndex].y = this.persons[bestIndex].y + bestGradient.point.y;
	
	//console.log('Best index: ' + bestIndex + ' gradient: ' + bestGradient.point);

	return;
};
	
/**
 * draws the AncestryTree on the Context
 */
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
	
/**
 * get the cursor position inside the AncestryTree
 *
 * @return {Point} cursor position inside the AncestryTree
 */
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
	
	return new Point(x, y);
};

// ///////////////////////////////////////////
//
// Module setup
//
// ///////////////////////////////////////////

if (typeof module === 'object' && module.exports) {
	module.exports.AncestryTree = AncestryTree;
	module.exports.Point = Point;
	module.exports.Relation = Relation;
	module.exports.Person = Person;
	module.exports.Rectangle = Rectangle;
}