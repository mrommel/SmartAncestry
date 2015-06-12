// installation: 
// * npm install gulp gulp-changed gulp-rename gulp-image-resize gulp-imagemin --save-dev
// * npm install --save-dev gulp-using
// 
// * TODO: https://github.com/rvagg/through2

var gulp = require('gulp');
var imageResize = require('gulp-image-resize');
var parallel = require("concurrent-transform");
var os = require("os");
var rename = require("gulp-rename");
var using = require('gulp-using');
// var ancestryTree = require('ancestryTree');

var fs          = require('fs');
var path        = require('path');
var through     = require('through2');
var Canvas      = require('canvas');
var PluginError = gutil.PluginError;

// define paths
var imgSrc = './data/media/persons/*',
    imgDst = 'data/media/persons_tree/';

gulp.task('default', function() {
	console.log("###################################################");
 	console.log("# run 'gulp resize' to resize all images          #");
 	console.log("###################################################");
});

gulp.task('resize', function() {
 	console.log("resize all images");

 	gulp.src(imgSrc)
 		.pipe(imageResize({ 
            width : 100,
            height : 100
        }))
        .pipe(gulpAncestryTree({ offsetX: 5 }))
        .pipe(gulp.dest(imgDst));
});

function gulpAncestryTree(opts) {

    // combine with default options
    opts = _.extend({
        offsetX: 0,
        offsetY: 0,
        width: 150,
        height: 70
    }, opts || {});

    return through.obj(function(file, enc, callback){
        // Pass file through if:
        // - file has no contents
        // - file is a directory
        if (file.isNull() || file.isDirectory()) {
            this.push(file);
            return callback();
        }
        // User's should be using a compatible glob with plugin.
        // Example: gulp.src('images/**/*.{jpg,png}').pipe(watermark())
        if (['.jpg', '.png'].indexOf(path.extname(file.path)) === -1) {
            this.emit('error', new PluginError({
                plugin: 'AncestryTree',
                message: 'Supported formats include JPG and PNG only.'
            }));
            return callback();
        }

        // No support for streams
        if (file.isStream()) {
            this.emit('error', new PluginError({
                plugin: 'AncestryTree',
                message: 'Streams are not supported.'
            }));
            return callback();
        }

        if (file.isBuffer()) {
            // create our virtual image
            // and set src to file's contents
            var img = new Canvas.Image();
            img.src = file.contents;
            
            // make a new canvas with the same dimensions
            var canvas = new Canvas(width, height);
            var ctx = canvas.getContext('2d');
            
            ctx.fillRect(0, 0, width, height);
            
            // fill the canvas with the initial image
            ctx.drawImage(img, offsetX, offsetY, height, height);
            
            // replace the file contents with our new image
            file.contents = canvas.toBuffer();

            this.push(file);
            return callback();
        }
    });
}