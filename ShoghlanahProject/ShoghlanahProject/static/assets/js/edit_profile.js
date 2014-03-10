$(document).ready(function () {
	$("#mobile_number").ForceNumericOnly();
	if($("#last_name").val() == "") {
		$('#save_button').attr('disabled','disabled');
		$("#last_name").addClass("ErrorField");
	}

	$('.tab').click(function (e) {
    	e.preventDefault();
    	$(this).tab('show');
    });
});