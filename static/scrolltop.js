$(document).ready(function(){
    $(window).scroll(function () {
      if ($(this).scrollTop() > 2000) {
                            $('#scroll-top').fadeIn();
                    } else {
                            $('#scroll-top').fadeOut();
                    }
            }); 
    $('#scroll-top').click(function(){
        $("html, body").animate({ scrollTop: 0 }, 600);
        return false;
    });
});
