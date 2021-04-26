function get_me_resource(post_data, callback_function){
    $.ajax({
        url: '/guardian/me/',
        data: post_data,
        type: 'post',
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        success: function(response){
            callback_function(response);
        }
    });
}

function data_for_date(d, callback_function) {
    get_me_resource({
        date: d,
        resource: '/data/for_date/'}, callback_function);
}

function choices_for_type(field_type, callback_function) {
    get_me_resource({
        type: field_type,
        resource: '/field/choices/'}, callback_function);
}