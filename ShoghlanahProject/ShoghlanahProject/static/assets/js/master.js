$(document).ready(function () {
    $('#mydrop a:not(:last)').css('border-bottom', '1px solid #cacaca');
    // $('.not a:not(:last)').css('border-bottom', '1px solid #cacaca');
    $("[rel=tooltip]").tooltip({'placement':'bottom', 'trigger' : 'hover' , 'animation' : 'true'});
    $('.dropdown-toggle').dropdown();
    $('input, textarea').placeholder();
    $('.Modalusers').click(function(){
        var $this = $(this);
        $.ajax({
          url: $this.attr('action'),
          type: "GET",
          success:function(data) {
            $('#chatContainer').html(data);
          },
        });
    });
    $("#q").focus(function(){
        $(this).attr("placeholder","");
    });
});

jQuery(function(){
    $("#search-button").click(function(){
        $(".error").hide();
        var hasError = false;
        var searchReg = /^[a-zA-Z0-9-]+$/;
        var searchVal = $("#q").val();

        if(searchVal == '') {
            hasError = true;
        } else if(!searchReg.test(searchVal)) {
            //$("#q").after('<span class="error">Enter valid text.</span>');
            //hasError = true;
        }
        if(hasError == true) {
            return false;
        }
    }); 
});


jQuery.fn.ForceNumericOnly =
function(extra)
{
    return this.each(function(extra)
    {
        $(this).keydown(function(e)
        {
            var key = e.charCode || e.keyCode || 0;
            // allow backspace, tab, delete, arrows, numbers and keypad numbers ONLY
            return (
                key == 8 || 
                key == 9 ||
                key == 46 ||
                (key >= 37 && key <= 40) ||
                (key >= 48 && key <= 57) ||
                (key >= 96 && key <= 105));
        });
    });
};

function load (id) {
                var loadingTest = $(id).attr("data-loading-text");
                $(id).attr("disabled","disabled");
                $(id).html(loadingTest);
            }

            function loading (id) {
                $(id).html('<div class="loadingbody"><span></span><span class="load-1"></span><span class="load-2"></span><span class="load-3"></span><span class="load-4"></span><span class="load-5"></span><span class="load-6"></span></div>');
            }


function test_name(value){
    var postname = $.trim(value);
    if(postname == "")
        return false;
    if (value.match(/\w/g).length >= 4)
        return true;
    else
        return false;
}
function test_mobile(value){
    var postname = $.trim(value);
    if(postname == "")
        return false;
    if (value.match(/^01[0-9]{9}$/))
        return true;
    else
        return false;
}
function test_int(value){
    var postname = $.trim(value);
    if(postname == "")
        return false;
    if (value.match(/[0-9]$/))
        return true;
    else
        return false;
}