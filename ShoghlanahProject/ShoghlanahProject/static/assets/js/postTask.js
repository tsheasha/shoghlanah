function formSubmit()
{
	if($('#postform').find('.ErrorField').length == 0){
		$("#postform").submit();
		loading('#loading');
	}else{
	
		$("#loading").html('<label class="general_imp">Fill the required fields (*)</label>');


	}
	
}

function disableEnterKey(e)
{
     var key;      
     if(window.event)
          key = window.event.keyCode; //IE
     else
          key = e.which; //firefox      

     return (key != 13);
}

$(document).ready(function () {	
	$('#postTask').on('shown', function () {
		final_update();
	});

	$("#sliderInput").ForceNumericOnly();

	$("#task_name").on('input', function(){
		if ($(this).val().length >= 128){
			$("#task_name_max_length").fadeIn();
		} else {
			$("#task_name_max_length").fadeOut();
		}
	});


	
});

function test_name(value){
	var postname = $.trim(value);
	if(postname == "")
		return false;
	if (value.match(/\w/g).length >= 4)
		return true;
	else
		return false;
}

jQuery(function(){
	jQuery("#task_name").validate({
		expression: "return test_name(VAL);",
	});
	jQuery("#gmaps-input-address").validate({
		expression: "return test_name(VAL);",
	});
});
	
