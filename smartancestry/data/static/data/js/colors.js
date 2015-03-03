var Colour = require('../Colour.js');

console.log("Loaded Colour");

var baseColor = new Colour.RGBColour(138, 86, 226);
var baseHue = Math.round(baseColor.getHSL().h);
var baseSat = Math.round(baseColor.getHSL().s);
var baseLum = Math.round(baseColor.getHSL().l);

//console.log("baseColor.h = " + baseHue);
//console.log("baseColor.s = " + baseSat);
//console.log("baseColor.l = " + baseLum);

console.log("current: 0 => " + baseColor.getCSSHexadecimalRGB());

var n = 12;
var step = (240.0 / n);

for (var i = 0; i < n; ++i) {
	//console.log("tmp: " + (baseHue + step * i)% 240.0);
	var currentColor = new Colour.HSLColour((baseHue + step * i) % 240.0, baseSat, baseLum);
	
	console.log("current: " + i + " => " + currentColor.getCSSHexadecimalRGB());
}



