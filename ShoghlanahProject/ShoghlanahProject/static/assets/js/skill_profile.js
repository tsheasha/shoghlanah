var professionals_clicked = false;
var shoghlanahs_clicked = false;

function professionals () {
	if (professionals_clicked) {
		professionals_clicked = false;
		$('#skill-stream').css("display","block");
		$('.tasks').css("display","block");
		$('#lower-container1').css("display","none");
	}
	else {
		professionals_clicked = true;
		shoghlanahs_clicked = false;
		$('#skill-stream').css("display","none");
		$('.tasks').css("display","none");
		$('#lower-container1').css("display","block");
		$('#dashboard').css("height",'100%');
	};
};

function shoghlanahs () {
	if (shoghlanahs_clicked) {
		shoghlanahs_clicked = false;
	}
	else {
		shoghlanahs_clicked = true;
		professionals_clicked = false;
		$('#skill-stream').css("display","block");
		$('#lower-container1').css("display","none");
		$('#dashboard').css("height",'100%');
	};
};
