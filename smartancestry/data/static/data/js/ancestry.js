var http = require('http'),
    url = require('url'),
    request = require('request'),
    fs = require('fs'),
    child_proc = require('child_process'),
    exec = require('child_process').exec;

http.createServer(function (req, res) {
  	res.writeHead(200, {'Content-Type': 'image/png'});
  	
  	var person_url = "http://127.0.0.1:8000/data/person/dot_tree/1/ancestry.dot";
  
  	request.get(person_url, function (error, response, body) {
  		if (!error && response.statusCode == 200) {
  	
  			// download file
  			fs.writeFile("tmp.dot", body, function(err) {
    			if(err) {
    				res.end();
        			return console.log("download error: " + err);
    			}
    			console.log("downloaded");
    			
    			// executes `dot`
				child = exec("dot -Tpng tmp.dot > tmp.png", function (error, stdout, stderr) {
					if (error !== null) {
						res.end();
						return console.log('exec error: ' + error);
					}
					console.log("executed");
				
					fs.readFile('tmp.png', function (err,data) {
						if (err) {
							res.end();
							return console.log(err);
						}
						console.log("loaded");
						res.write(data);
						res.end();
					});
				});
			}); 
  		} else {
  			res.end();
  		}
	});
}).listen(4446, '127.0.0.1');
 
console.log('Ancestry SVG server running at http://127.0.0.1:4446/');
console.log('ex. http://127.0.0.1:4446/?values=.4,.3,.2,.1');