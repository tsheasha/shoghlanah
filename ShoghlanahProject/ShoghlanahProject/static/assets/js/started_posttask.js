$(document).ready(function () {
	var position;
	getLocation(function(latlng){
		position = latlng.split(',');
		json_map = map_initialize(position[0], position[1],true,'gmap');
		switchMap(json_map.marker,json_map.map,"#gmaps-input",'#gmaps-latitude','#gmaps-longitude');
     });

	$("#trig_paid").click( function(){
		$("#badge_div").slideUp("fast", function() {
    		$("#slide_div").slideDown("fast");
    		
  		});
  		if($('#taskdesc').hasClass('ErrorField')){
	  		jQuery('#taskdesc').prev().remove();
	  		jQuery('#taskdesc').removeClass('ErrorField');
  		}
	}); 

	$("#slideInput").ForceNumericOnly();

});

jQuery(function(){
		jQuery("#taskname").validate({
			expression: "return test_task_name(VAL);",
		});
		jQuery("#gmaps-input").validate({
			expression: "if (VAL) return true; else return false;",
		});
	});