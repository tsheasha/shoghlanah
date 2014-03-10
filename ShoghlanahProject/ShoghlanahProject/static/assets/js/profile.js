$(document).ready(function() {
	Shadowbox.init({
	});
	var x = $('#profile-gallery-follow').height();
	$("#lower-container").css('min-height',x);
});

// $("#about-div").jReadMore({
//     open: 'Read Less',
//     close: 'Read More',
//     height: 80, 
//     diff: 20 //if the height of the opened section is smaller than 40, don't apply plugin
// });
var followers_clicked = false;
var reviews_clicked = false;
var tasks_clicked = false;
var following_clicked = false;

function followers () {
	if (followers_clicked) {
		followers_clicked = false;
		$('.product_container').css("display","block");
		$('#profile-stream').css("display","block");
		$('#lower-container1').css("display","none");
		$('#lower-container2').css("display","none");
		$('#lower-container3').css("display","none");
		$('#lower-container4').css("display","none");
	}
	else {
		//$('#lower-container').remove();
		followers_clicked = true;
		reviews_clicked = false;
		tasks_clicked = false;
		following_clicked = false;
		$('#profile-stream').css("display","none");
		$('.product_container').css("display","none");
		$('#lower-container1').css("display","block");
		$('#lower-container2').css("display","none");
		$('#lower-container3').css("display","none");
		$('#lower-container4').css("display","none");
		//c.append(lc);
		//$('#lower-container1').css("visibility","visible");
		$('#dashboard').css("height",'100%');
	};
};
function reviews () {
	if (reviews_clicked) {
		reviews_clicked = false;
		$('#profile-stream').css("display","block");
		$('.product_container').css("display","block");
		$('#lower-container2').css("display","none");
		$('#lower-container1').css("display","none");
		$('#lower-container3').css("display","none");
		$('#lower-container4').css("display","none");

	} 
	else{
		reviews_clicked = true;
		followers_clicked = false;
		tasks_clicked = false;
		following_clicked = false;
		//$('#lower-container').remove();
		$('#profile-stream').css("display","none");
		$('.product_container').css("display","none");
		$('#lower-container2').css("display","block");
		$('#lower-container1').css("display","none");
		$('#lower-container3').css("display","none");
		$('#lower-container4').css("display","none");
		//c.append(lc);
		//$('#lower-container1').css("visibility","visible");
		$('#dashboard').css("height",'100%');
	};
};
function tasks () {
	if (tasks_clicked) {
		tasks_clicked = false;
		$('#profile-stream').css("display","block");
		$('.product_container').css("display","block");
		$('#lower-container2').css("display","none");
		$('#lower-container1').css("display","none");
		$('#lower-container3').css("display","none");
		$('#lower-container4').css("display","none");
	} 
	else{
		tasks_clicked = true;
		followers_clicked = false;
		reviews_clicked = false;
		following_clicked = false;
		//$('#lower-container').remove();
		$('#profile-stream').css("display","none");
		$('.product_container').css("display","none");
		$('#lower-container2').css("display","none");
		$('#lower-container1').css("display","none");
		$('#lower-container3').css("display","block");
		$('#lower-container4').css("display","none");
		//c.append(lc);
		//$('#lower-container1').css("visibility","visible");
		$('#dashboard').css("height",'100%');
	};
};
function following () {
	if (following_clicked) {
		following_clicked = false;
		$('#profile-stream').css("display","block");
		$('.product_container').css("display","block");
		$('#lower-container1').css("display","none");
		$('#lower-container2').css("display","none");
		$('#lower-container3').css("display","none");
		$('#lower-container4').css("display","none");
	}
	else {
		//$('#lower-container').remove();
		following_clicked = true;
		reviews_clicked = false;
		tasks_clicked = false;
		followers_clicked = false;
		$('#profile-stream').css("display","none");
		$('.product_container').css("display","none");
		$('#lower-container1').css("display","none");
		$('#lower-container2').css("display","none");
		$('#lower-container3').css("display","none");
		$('#lower-container4').css("display","block");
		//c.append(lc);
		//$('#lower-container1').css("visibility","visible");
		$('#dashboard').css("height",'100%');
	};
};