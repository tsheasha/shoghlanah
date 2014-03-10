var selectedfilter = '';
var mainHtml = '';
function remove_task(task_id){
    $('#dashboard').css("height",$('#dashboard').height()-$('.task'+task_id).height());
    $('#v-gradient').css("height",$('#v-gradient').height()-$('.task'+task_id).height());
    $('.task'+task_id).fadeOut(500);
    $('#timestamp'+task_id).fadeOut(500);
};

function remove_follow(follow_id){
    $('#dashboard').css("height",$('#dashboard').height()-$('.follow'+follow_id).height());
    $('#v-gradient').css("height",$('#v-gradient').height()-$('.follow'+follow_id).height());
    $('.follow'+follow_id).fadeOut(500);
    $('#timestamp'+follow_id).fadeOut(500);
};

$(window).scroll(function() {
    if($(window).scrollTop() + $(window).height() >= ($(document).height())*0.8) {       
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
