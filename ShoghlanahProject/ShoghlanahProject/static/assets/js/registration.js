$(document).ready(function() { 
 
    $('#signup').click(function() {  
 
        $(".error").hide();
        var hasError = false;
        var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
 
        var emailaddressVal = $("#id_email").val();
        if(emailaddressVal == '') {
            $("#id_email").before('<span class="error"><font color="red">Please Enter Your Email Address.</font></span>');
            hasError = true;
        }
 
        else if(!emailReg.test(emailaddressVal)) {
            $("#id_email").before('<span class="error"><font color="red">Enter  Valid Email Address.</font></span>');
            hasError = true;
        }

        var nameReg = /^[A-Za-z\u0600-\u065F\u066A-\u06EF\u06FA-\u06FF\s]+$/;
        var firstname = $("#id_first_name").val();
        var lastname = $("#id_last_name").val();
        if(lastname == '' && firstname == '') {
            $("#fullname").before('<span class="error"><font color="red">Please Enter Your Full Name.</font></span>');
            hasError = true;
        }

        else if(firstname == '') {
            $("#fullname").before('<span class="error"><font color="red">Please Enter Your First Name.</font></span>');
            hasError = true;
        }

        else if(lastname == '') {
            $("#fullname").before('<span class="error"><font color="red">Please Enter Your Last Name.</font></span>');
            hasError = true;
        }

        else if(!nameReg.test(document.getElementById("id_first_name").value) && !nameReg.test(document.getElementById("id_last_name").value)) {
            $("#fullname").before('<span class="error"><font color="red">Enter a Valid Full Name.</font></span>');
            hasError = true;
        }

        else if(!nameReg.test(document.getElementById("id_first_name").value)) {
            $("#fullname").before('<span class="error"><font color="red">Enter a Valid First Name.</font></span>');
            hasError = true;
        }

        else if(!nameReg.test(document.getElementById("id_last_name").value)) {
            $("#fullname").before('<span class="error"><font color="red">Enter a Valid Last Name.</font></span>');
            hasError = true;
        }

        var password = $("#id_password").val();
        if(password == '') {
            $("#id_password").before('<span class="error"><font color="red">Please Enter Your Password.</font></span>');
            hasError = true;
        }
 
        if(hasError == true) { return false; }
 
    });



});

