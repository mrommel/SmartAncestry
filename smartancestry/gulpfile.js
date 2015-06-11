var gulp = require('gulp');
var imageResize = require('gulp-image-resize');

gulp.task('default', function() {
	console.log("###################################################");
 	console.log("# run 'gulp resize' to resize all images          #");
 	console.log("###################################################");
});

gulp.task('resize', function() {
 	console.log("resize all images");
 	
 	// define paths
	var imgSrc = './originals/**/*',
        imgDst = './optimized/';
 	
 	gulp.watch(imgSrc, ['thumb']);
});

gulp.task('thumb', function () {
    gulp.src(imgSrc)
        .pipe(imageResize({ 
            width : 100,
            height : 100,
            crop : true,
            upscale : false,
            imageMagick: true
        }))
        .pipe(imagemin())
        .pipe(rename({suffix: '-thumb'}))
        .pipe(gulp.dest(imgDst));
});