// Function to get value from a cookie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    if (cookieValue === null){
        console.log('!~!~!~! cookie for ' + name + ' is null !~!~!~!');
    }
    return cookieValue;
}

function refresh_list(field_type, $select, placeholder){
    choices_for_type(field_type, function(response){
            $select.select2({
                data: response.data.choices,
                allowClear: false,
                multiple: false,
                closeOnSelect: true,
                //not sure this is working
                scrollAfterSelect: true,
                placeholder: placeholder});
    });
}

function time_from_seconds(seconds) {
    var hours   = Math.floor(seconds / 3600);
    var minutes = Math.floor((seconds - (hours * 3600)) / 60);
    var seconds = seconds - (hours * 3600) - (minutes * 60);

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    return hours+':'+minutes+':'+seconds;
}

function add_alerts($alert, msg_list){
    msg_list.forEach(function(msg, index){
       add_alert($alert, msg.type, msg.text);
    });
}

function add_alert($alert_div, type, msg){
    var alert = $('<div>');
    switch(type){
        case 'error':
            alert.addClass('alert-danger');
            break;
        case 'info':
            alert.addClass('alert-info');
            break;
        case 'warning':
            alert.addClass('alert-warning');
            break;
        default:
            alert.addClass('alert-dark');    }
    alert.addClass('alert alert-dismissable fade show small');
    alert.text(msg);
    alert.append($('<button>').attr({type: 'button',
                                     class: 'close',
                                     'data-dismiss': 'alert'}).text('x'));
    $alert_div.append(alert);
}