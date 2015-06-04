var http = require('http'),
    url = require('url'),
    jsdom = require('jsdom'),
    request = require('request'),
    viz = require('../viz.js'),
    fs = require('fs'),
    child_proc = require('child_process'),
    w = 400,
    h = 400,
    scripts = ["file://"+__dirname+"/d3.min.js",
               "file://"+__dirname+"/d3.layout.min.js",
               "file://"+__dirname+"/pie.js"],
    htmlStub = '<!DOCTYPE html><div id="pie" style="width:'+w+'px;height:'+h+'px;"></div>';

http.createServer(function (req, res) {
  	res.writeHead(200, {'Content-Type': 'image/png'});
  	var convert = child_proc.spawn("convert", ["svg:", "png:-"]),
      	values = (url.parse(req.url, true).query['values'] || ".5,.5")
        .split(",")
        .map(function(v){return parseFloat(v)});
 
  	convert.stdout.on('data', function (data) {
    	res.write(data);
  	});
  	convert.on('exit', function(code) {
    	res.end();
  	});
  
  	var person_url = "http://127.0.0.1:8000/data/person/dot_tree/1/";
  
  	request.get(person_url, function (error, response, body) {
  		if (!error && response.statusCode == 200) {
  		
  			//console.log('---------------');
  			//console.log(body);
  			//console.log('---------------');

    		// circo dot fdp neato nop nop1 nop2 osage patchwork twopi
    		var svgsrc = viz.Viz(body, 'svg', "dot");
    		convert.stdin.write(svgsrc);
    		convert.stdin.end();
  		} else {
  			console.log('error: ' + error + ', ' + response.statusCode);
  			convert.stdin.end();
  		}
	});
}).listen(4446, '127.0.0.1');
 
console.log('Ancestry SVG server running at http://127.0.0.1:4446/');
console.log('ex. http://127.0.0.1:4446/?values=.4,.3,.2,.1');