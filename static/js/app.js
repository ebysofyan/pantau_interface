(function ($) {
    $(function () {

        $('.sidenav').sidenav();
        $('select')
            .not('.disabled')
            .formSelect();

    }); // end of document ready
})(jQuery); // end of jQuery name space
