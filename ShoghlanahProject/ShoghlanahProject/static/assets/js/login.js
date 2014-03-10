$(document).ready(function() { 
 
    $('#login-btn').click(function() {  
 
        $(".error").hide();
        var hasError = false;
        var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
 
        var emailaddressVal = $("#username").val();
        if(emailaddressVal == '') {
            $("#username").before('<span class="error"><font color="red">Please Enter Your Email.</font></span>');
            hasError = true;
        }
 
        else if(!emailReg.test(emailaddressVal)) {
            $("#username").before('<span class="error"><font color="red">Enter A Valid Email Address.</font></span>');
            hasError = true;
        }

        var password = $("#password").val();
        if(password == '') {
            $("#password").before('<span class="error"><font color="red">Please Enter Your Password.</font></span>');
            hasError = true;
        }
 
        if(hasError == true) { return false; }
 
    });



});

