filter_check = true;
var selectedfilter='';
var mainHtml = '';
$(document).ready(function(){
    $('#dashboard').css("height",$(document).height()-100);
    $('#v-gradient').css("height", $('#dashboard').height() - $('#info').height()-100);
    $('input:radio[name=dock_radio]').click(function() {
        var value = $(this).val();
        selectedfilter = $(this)
        filter(value);
    });
    $('.dock').css({'display':'none'});
    mainHtml = $("#stream").html();
});


function show_more(){

if(filter_check) {
$("#more").html('<img src="' + window.static_url_new +'img/loading_stream.gif" />');
$.ajax({
    type: "POST",
    url:"/more/",
    data: "discover=1&to_add="+$('div#stream div#singleton').length,
        success: function(req){
            $("#more").html('');
            if(req.length > 50) {
                    $('#stream').append(req);
                    }
            if(req.length > 50) {
                $('#dashboard').css("height",$(document).height());
                $('#v-gradient').css("height", $('#dashboard').height() - $('#info').height());
            }
        }
    });
    }
};

function filter(verb){
filter_check = false;
$.ajax({
    type: "POST",
    url:"/filter/",
    data: "discover=1&verb="+verb,
        success: function(req){
        $('#stream').html(req);
            if(req.length > 50) {
                $('#dashboard').css("height",$(document).height());
                $('#v-gradient').css("height", $('#dashboard').height() - $('#info').height());
            }
        }
    });
}; 

function load_latest(){
$.ajax({
    type: "POST",
    url:"/latest/",
        success: function(req){
            var prev = $(document).height();
            $('#stream').prepend(req);
            if(req.length > 50) {
                $('#dashboard').css("height",$(document).height());
                $('#v-gradient').css("height", $('#dashboard').height() - $('#info').height());
            }
        }
    });
};

function remove_task(task_id){
    $('#dashboard').css("height",$('#dashboard').height()-$('.'+task_id).height());
    $('#v-gradient').css("height",$('#v-gradient').height()-$('.'+task_id).height());
    $('.'+task_id).fadeOut(500);
};

$(window).scroll(function() {
    if($(window).scrollTop() + $(window).height() >= $(document).height()) {       
        if ($('div#stream div#singleton').length > 9)
            show_more();
    }
});

function showfilters(){
    if($('.dock').is(":hidden")){
        $('.dock').show('slide', {direction: 'right'}, 1500);
        $('#filtericon').css({'border-radius':'35px','border-bottom-left-radius': '0px', 'border-top-left-radius': '0px'});
        $('#Ifilter').toggleClass('icon-filter  icon-remove');
        mainHtml = $("#stream").html();
    }
    else{
        $('.dock').hide('slide', {direction: 'right'}, 500,function(){
            if(selectedfilter !== ''){
                selectedfilter.attr("checked", false);
            }
            $('#filtericon').css({'border-radius':'35px','border-bottom-left-radius': '35px', 'border-top-left-radius': '35px'});
            $('#Ifilter').toggleClass('icon-filter  icon-remove');
        }); 
        $('#stream').html(mainHtml); 
    }   
};
