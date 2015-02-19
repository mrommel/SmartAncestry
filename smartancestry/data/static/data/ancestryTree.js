
var Relation = function(source, destination) {
	this.source = source;
	this.destination = destination;
};
				
Relation.prototype = {
	getSourcePerson: function(persons) {
		var person;

		for (index = 0; index < persons.length; ++index) {
			if (persons[index].id == this.source) {
				person = persons[index];
			}
		}
		
		return person;
	},
	
	getDestinationPerson: function(persons) {
		var person;

		for (index = 0; index < persons.length; ++index) {
			if (persons[index].id == this.destination) {
				person = persons[index];
			}
		}
		
		return person;
	},
	
	draw: function(context, persons) {
		var cell1 = this.getSourcePerson(persons).getSource();
		var cell2 = this.getDestinationPerson(persons).getDestination();
		var x0 = (cell1.x + cell2.x) / 2; 
		
		context.beginPath();
		context.moveTo(cell1.x, cell1.y);
		context.lineTo(x0, cell1.y);
		context.lineTo(x0, cell2.y);
		context.lineTo(cell2.x, cell2.y);
		context.strokeStyle = "#000";
		context.stroke();
	},
};

var Person = function(id, name, birth, death) {
	this.id = id;
	this.name = name;
	this.birth = birth;
	this.death = death;
	
	this.x = 0;
	this.y = 0;
	this.width = 0;
	this.height = 0;
	this.selected = false;
};

Person.prototype = {			
	getDestination: function() {
		return new Cell(this.x, this.y + this.height / 2);
	},
	
	getSource: function() {
		return new Cell(this.x + this.width, this.y + this.height / 2);
	},
	
	getInfo: function() {
		return this.name;
	},
	
	draw: function(context) {
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
	},
	
	toString: function() {
		return '[Person id:' + this.id + ' ,name:' + this.name + ' ,x:' + this.x + ' ,y:' + this.y + ']';
	},
};

var Cell = function(x, y) {
	this.x = x;
	this.y = y;
};

Cell.prototype = {
	getPerson: function(persons) {
		var person;

		for (index = 0; index < persons.length; ++index) {
			if(persons[index].x <= this.x && this.x <= (persons[index].x + personWidth) && persons[index].y <= this.y && this.y <= (persons[index].y + personHeight)) {
				person = persons[index];
			}
		}
		return person;
	},
	
	getInfo: function() {
		return 'Cell(' + this.x + ', ' + this.y + ')';
	},
};

var personWidth = 150;
var personHeight = 44;

function AncestryTree(canvasContext, personData, relationData) {
	this.context = canvasContext;

	this.personData = personData;
	this.relationData = relationData;

	this.width = this.context.canvas.width;
	this.height = this.context.canvas.height;
	
	this.persons = [];
	
	this.initialize();
}

AncestryTree.prototype.initialize = function() {
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
		/*var name = entry.name;
		name = name.replace('&lt;u&gt;', '');
		name = name.replace('&lt;/u&gt;', '');
		name = name.replace('&amp;auml;', 'ä');
		name = name.replace('  ', ' ');
		name = name.replace('  ', ' ');*/
		
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

