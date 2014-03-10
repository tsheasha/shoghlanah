$(function(){
	$("#order_quantity").validate({
		expression: "return test_int(VAL);",
	});
	$("#order_address").validate({
		expression: "return test_name(VAL);",
	});
	$("#order_mobile_number").validate({
		expression: "return test_mobile(VAL);",
	});
	$("#order_quantity").ForceNumericOnly();
	$("#order_mobile_number").ForceNumericOnly();

    $("#up").on('click',function(){
    	var currentVal = parseInt($("#incdec input").val());
    	if (!isNaN(currentVal)) {
           $("#incdec input").val(parseInt(currentVal+1));
        } else {
           $("#incdec input").val(1);
        }
        $('#order_quantity').trigger('change');
    });

    $("#down").on('click',function(){
    	var currentVal = parseInt($("#incdec input").val());
    	if (!isNaN(currentVal) && currentVal > 1) {
           $("#incdec input").val(parseInt(currentVal-1));
        } else {
           $("#incdec input").val(1);
        }
        
        $('#order_quantity').trigger('change');
    });
});