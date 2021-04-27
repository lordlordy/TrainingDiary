function get_anyone_resource(post_data, callback_function){
    $.ajax({
        url: '/guardian/anyone/',
        data: post_data,
        type: 'post',
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        success: function(response){
            callback_function(response);
        }
    });
}

function bike_summary(callback_function) {
    get_anyone_resource({
        resource: '/bike/summary/'}, callback_function);
}

function training_summary(callback_function) {
    get_anyone_resource({
        resource: '/training/summary/'}, callback_function);
}

function graph_data(graph, year, activity, callback_function) {
    get_anyone_resource({
        'graph': graph,
        'year': year,
        'activity': activity,
        resource: '/training/data/canned/'}, callback_function);
}