$(function () {
	$("div.product").hover(
	  function () {
	    $(this).children('.information_box').css("background-color","rgba(239, 239, 242, .8)");
	    $(this).children('.information_box').css("color","#f3592a");
	    $(this).children('.information_box').css("color","#ff0000")
	  },
	  function () {
	    $(this).children('.information_box').css("background-color","rgba(31, 88, 123, .8)");
	    $(this).children('.information_box').css("color","#ffffff");
	  }
	);
});