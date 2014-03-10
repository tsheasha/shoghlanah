/**
 * @author GeekTantra
 * @date 20 September 2009
 */

 /**
 * @author Salma
 * added a feature to support validation in special cases
 * like validation in case of radio button only selected
 */
(function(jQuery){
    var ValidationErrors = new Array();
    jQuery.fn.validate = function(options){
        options = jQuery.extend({
            expression: "return true;",
            message: "",
            error_class: "ValidationErrors",
            error_field_class: "ErrorField",
            selected:"",
            live: true
        }, options);
        var SelfID = jQuery(this).attr("id");
        var unix_time = new Date();
        unix_time = parseInt(unix_time.getTime() / 1000);
        if (!jQuery(this).parents('form:first').attr("id")) {
            jQuery(this).parents('form:first').attr("id", "Form_" + unix_time);
        }
        var FormID = jQuery(this).parents('form:first').attr("id");
        if (!((typeof(ValidationErrors[FormID]) == 'object') && (ValidationErrors[FormID] instanceof Array))) {
            ValidationErrors[FormID] = new Array();
        }
        if (options['live']) {
            if (jQuery(this).find('input').length > 0) {
                jQuery(this).find('input').bind('blur', function(){
                    if (validate_field("#" + SelfID, options)) {
                        if (options.callback_success) 
                            options.callback_success(this);
                    }
                    else {
                        if (options.callback_failure) 
                            options.callback_failure(this);
                    }
                });
                jQuery(this).find('input').bind('focus keypress click', function(){
                    jQuery("#" + SelfID).prev('.' + options['error_class']).remove();
                    jQuery("#" + SelfID).removeClass(options['error_field_class']);
                });
            }
            else {
                jQuery(this).bind('blur', function(){
                    validate_field(this);
                });
                jQuery(this).bind('focus keypress', function(){
                    jQuery(this).prev('.' + options['error_class']).fadeOut("fast", function(){
                        jQuery(this).remove();
                    });
                    jQuery(this).removeClass(options['error_field_class']);
                });
            }
        }
        jQuery(this).parents("form").submit(function(){
            if (validate_field('#' + SelfID)) 
                return true;
            else 
                return false;
        });
        function validate_field(id){
            var self = jQuery(id).attr("id");
            var expression = 'function Validate(){' + options['expression'].replace(/VAL/g, 'jQuery(\'#' + self + '\').val()') + '} Validate()';
            var validation_state = eval(expression);
            if (!validation_state) {
                if (jQuery(id).prev('.' + options['error_class']).length == 0) {
                    if(options['selected'] == ''){
                        jQuery(id).before('<span class="' + options['error_class'] + '">' + options['message'] + '</span>');
                        jQuery(id).addClass(options['error_field_class']);
                    }
                    else{
                        if($(options['selected']).is(':checked')){
                            jQuery(id).before('<span class="' + options['error_class'] + '">' + options['message'] + '</span>');
                            jQuery(id).addClass(options['error_field_class']);
                        }
                    }
                }
                if (ValidationErrors[FormID].join("|").search(id) == -1) 
                    if(options['selected'] == ''){
                        ValidationErrors[FormID].push(id);
                    }
                    else{
                        if($(options['selected']).is(':checked')){
                            ValidationErrors[FormID].push(id);
                        }
                        else{
                            ValidationErrors[FormID].pop(id);
                            return true;
                        }
                    }
                return false;
            }
            else {
                for (var i = 0; i < ValidationErrors[FormID].length; i++) {
                    if (ValidationErrors[FormID][i] == id) 
                        ValidationErrors[FormID].splice(i, 1);
                }
                return true;
            }
        }
    };
    jQuery.fn.validated = function(callback){
        jQuery(this).each(function(){
            if (this.tagName == "FORM") {
                jQuery(this).submit(function(){
                    if (ValidationErrors[jQuery(this).attr("id")].length == 0) 
                        callback();
					return false;
                });
            }
        });
    };
})(jQuery);
