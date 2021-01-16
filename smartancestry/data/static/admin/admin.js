
(function($) {
    'use strict';
    $(document).ready(function() {
        var gender = $("#id_sex").val();
        console.log('check for gender: ' + gender);

        if (gender == 'M') {
            $("#Ehefrau-group").hide();
            $("#Ehemann-group").show();
        } else {
            $("#Ehefrau-group").show();
            $("#Ehemann-group").hide();
        }

        $('#id_sex').change(function() {
            var gender = $("#id_sex").val();
            console.log('gender changed: ' + gender);

            if (gender == 'M') {
                $("#Ehefrau-group").hide();
                $("#Ehemann-group").show();
            } else {
                $("#Ehefrau-group").show();
                $("#Ehemann-group").hide();
            }
        });
    });
})(django.jQuery);