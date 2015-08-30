'use strict';

var gulp = require('gulp');
var sass = require('gulp-sass');
var gulpCopy = require('gulp-copy');

var paths = {
  sass: './styles/**/*.scss',
  staticOut: './static',
  styles: './static/styles',
  bower: ['bower_components/**/*.css', 'bower_components/**/*.js']
};

gulp.task('sass', function () {
  gulp.src(paths.sass)
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest(paths.styles));
});

gulp.task('bower', function() {
  return gulp.src(paths.bower)
    .pipe(gulpCopy(paths.staticOut))
});

gulp.task('watch', function() {
  gulp.watch(paths.sass, ['sass']);
  gulp.watch(paths.bower, ['bower']);
});

gulp.task('default', ['sass', 'bower', 'watch']);