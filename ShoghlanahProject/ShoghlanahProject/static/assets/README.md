the css, icons, images and js folders in this folder 'assets' should only include files to be used in our html files, and their format should be as follows:

for "master.html", all js scripts written in it should be put in master.js in 'static/assets/js' folder same applies for any css in the file, also should be put in master.css in 'static/assets/css/'
and import those 2 files like we import other files:
<script src="{{STATIC_URL}}assets/js/master.js"></script>
<link rel="stylesheet" href="{{STATIC_URL}}assets/css/master.css">

note: keep in mind the conventions for writing js and css in a separate file
