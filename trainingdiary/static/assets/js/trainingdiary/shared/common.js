LONG_MONTHS = ['January', 'February', 'March', 'April' , 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
SHORT_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr' , 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

$(document).ready(function () {

    $("#logout").on('click', function(){
        logout(function(response){
            window.location.href='index.html';
        })
    });
});


$('#login_form').submit(function () {
    $.ajax({
        data: $(this).serialize(),
        type: $(this).attr('method'),
        url: '/login/',
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        success: login_success
    });
    return false;
});

function login_success(response) {
    console.log(response);
    if (response.status) {
        window.location.href='index.html';
    }
}


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

function refresh_list(field_type, include_all, $select, placeholder, callback_function){
    choices_for_type(field_type, include_all, function(response){
            $select.select2({
                data: response.data.choices,
                allowClear: false,
                multiple: false,
                closeOnSelect: true,
                //not sure this is working
                scrollAfterSelect: true,
                placeholder: placeholder});
            callback_function(response);
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

function seconds_from_time(time) {
    let parts = time.split(":")
    return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2])
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

function create_series_form(form_id) {
    refresh_list('measure', false, $("#measure"), "Select measure", function(response){$("#measure").val('miles').trigger('change')});
    refresh_list('activity', true, $("#activity"), "Select type", function(response){$("#activity").val('Bike').trigger('change')});
    refresh_list('activityType', true, $("#activity_type"), "Select type", function(response){$("#activity_type").val('All').trigger('change')});
    refresh_list('equipment', true, $("#equipment"), "Select type", function(response){$("#equipment").val('All').trigger('change')});
    refresh_list('dayType', true, $("#day_type"), "Select type", function(response){$("#day_type").val('All').trigger('change')});
    refresh_list('period', true, $("#period"), "Select type", function(response){$("#period").val('Day').trigger('change')});
    refresh_list('aggregation', false, $("#period_aggregation"), "Select type", function(response){$("#period_aggregation").val('Sum').trigger('change')});
    refresh_list('aggregation', false, $("#rolling_aggregation"), "Select type", function(response){$("#rolling_aggregation").val('Sum').trigger('change')});
    refresh_list('day_aggregation', false, $("#day_aggregation"), "Select type", function(response){$("#day_aggregation").val('Sum').trigger('change')});
    refresh_list('processor', false, $("#processor_type"), "Select type", function(response){$("#processor_type").val('Lifetime Eddington').trigger('change')});
    refresh_list('interpolation', false, $("#interpolation"), "Select type", function(response){$("#interpolation").val('zero').trigger('change')});

    $("#day_of_week").select2({
        data: [
            {text: "All", id: "All"},
            {text: "Monday", id: "Monday"},
            {text: "Tuesday", id: "Tuesday"},
            {text: "Wednesday", id: "Wednesday"},
            {text: "Thursday", id: "Thursday"},
            {text: "Friday", id: "Friday"},
            {text: "Saturday", id: "Saturday"},
            {text: "Sunday", id: "Sunday"},
        ],
        closeOnSelect: true});
    $("#day_of_week").val('All').trigger('change');

    $("#month").select2({
        data: [
            {text: "All", id: "All"},
            {text: "January", id: "January"},
            {text: "February", id: "February"},
            {text: "March", id: "March"},
            {text: "April", id: "April"},
            {text: "May", id: "May"},
            {text: "June", id: "June"},
            {text: "July", id: "July"},
            {text: "August", id: "August"},
            {text: "September", id: "September"},
            {text: "October", id: "October"},
            {text: "November", id: "November"},
            {text: "December", id: "December"},
        ],
        closeOnSelect: true});
    $("#month").val('All').trigger('change');

    const yesNo = {
        data: [{text: 'yes', id: 'yes'}, {text: 'no', id: 'no'}], 
        closeOnSelect: true,
        // this removes search box
        minimumResultsForSearch: -1
    }

    $("#to_date").select2(yesNo);
    $("#to_date").val('no').trigger('change');
    $("#rolling").select2(yesNo);
    $("#rolling").val('no').trigger('change');
    $("#period_include_zeroes").select2(yesNo);
    $("#period_include_zeroes").val('yes').trigger('change');
    $("#rolling_include_zeroes").select2(yesNo);
    $("#rolling_include_zeroes").val('yes').trigger('change');

}