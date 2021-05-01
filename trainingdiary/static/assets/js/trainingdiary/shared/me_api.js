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

function data_for_between(data_type, from_date, to_date, callback_function) {
    get_me_resource({
        'data_type': data_type,
        'from_date': from_date,
        'to_date': to_date,
        resource: '/data/for_dates/'}, callback_function);
}

function next_diary_date(callback_function) {
    get_me_resource({
        resource: '/data/next_diary_date/'}, callback_function);
}

function choices_for_type(field_type, callback_function) {
    get_me_resource({
        type: field_type,
        resource: '/field/choices/'}, callback_function);
}

function save_day(date, day_type, comments, callback_function) {
    get_me_resource({
        'date': date,
        'day_type': day_type,
        'comments': comments,
        resource: '/save/day/'}, callback_function);
}

function readings_left(date, callback_function) {
    get_me_resource({
        'date': date,
        resource: '/readings/left_for_date/'}, callback_function);
}

function save_readings(date, json, callback_function) {
    get_me_resource({
        'date': date,
        'json': json,
        resource: '/readings/new/save/'}, callback_function);
}

function save_workout(json, callback_function) {
    get_me_resource({
        'json': json,
        resource: '/workout/save/'}, callback_function);
}

function delete_workout(pk, callback_function) {
    get_me_resource({
        primary_key: pk,
        resource: '/workout/delete/'}, callback_function);
}

function delete_reading(pk, callback_function) {
    get_me_resource({
        primary_key: pk,
        resource: '/reading/delete/'}, callback_function);
}