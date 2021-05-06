var $day_table;
var $reading_table;
var $workout_table;
var $new_reading_table

$(document).ready(function () {

    refresh_list('activity', false, $("#activity"), "Select activity", function(response){});
    refresh_list('activityType', false, $("#activity_type"), "Select activity type", function(response){});
    refresh_list('equipment', false, $("#equipment"), "Select equipment", function(response){});
    refresh_list('tssMethod', false, $("#tss_method"), "Select method", function(response){});
    refresh_list('dayType', false, $("#day_type_select"), "Select type", function(response){});

    const today = new Date();
    let from_date = new Date();
    from_date.setDate(from_date.getDate() - 7);
    let from_str = from_date.toLocaleDateString('en-CA');
    let to_str = today.toLocaleDateString('en-CA');
    $("#day_from, #reading_from, #workout_from").val(from_str);
    $("#day_to, #reading_to, #workout_to, #new_readings_date").val(to_str);

    $("#day_waiting, #reading_waiting, #workout_waiting").removeClass('hide');
    
    data_for_between('Day', from_str, to_str, function(response){
        add_alerts($("#day_alerts"), response.messages);
        $("#day_waiting").addClass('hide');
        if (response.status === 'success') {
            populate_days(response.data.instances)
        }
    });

    data_for_between('Reading', from_str, to_str, function(response){
        add_alerts($("#reading_alerts"), response.messages);
        $("#reading_waiting").addClass('hide');
        if (response.status === 'success') {
           populate_readings(response.data.instances);
        }
    });

    data_for_between('Workout', from_str, to_str, function(response){
        add_alerts($("#workout_alerts"), response.messages);
        $("#workout_waiting").addClass('hide');
        if (response.status === 'success') {
            populate_workouts(response.data.instances);
        }
    });

    $("#day_from, #day_to, #reading_from, #reading_to, #workout_from, #workout_to").on('blur', function(){
        const dataType = $(this).attr('data-type');
        switch (dataType) {
            case 'Day':
                $("#day_waiting").removeClass('hide');
                data_for_between('Day', $("#day_from").val(), $("#day_to").val(), function(response){populate_days(response.data.instances)});
                break;
            case 'Reading':
                $("#reading_waiting").removeClass('hide');
                data_for_between('Reading', $("#reading_from").val(), $("#reading_to").val(), function(response){populate_readings(response.data.instances)});
                break;
            case 'Workout':
                $("#workout_waiting").removeClass('hide');
                data_for_between('Workout', $("#workout_from").val(), $("#workout_to").val(), function(response){populate_workouts(response.data.instances)});
                break;   
        }
    });

    $("#add_next_day").on('click', function(){
        next_diary_date(function(response){
            $("#day_type_select").val('Normal').trigger('change');
            $("#date").val(response.data.next_date);
            $("#day_modal").modal('show');
        });
    });

    $("#day_table").on('dblclick', 'tbody tr', function(){
        let data = $day_table.row($(this)).data();
        $("#date").val(data.date);
        $("#day_type_select").val(data.day_type).trigger('change');
        $("#comments").val(data.comments);
        $("#day_modal").modal('show');
    });

    $("#save_day").on('click', function(){
        save_day($("#date").val(), $("#day_type_select").val(), $("#comments").val(), function(response){
            add_alerts($("#day_alerts"), response.messages);
            $("#day_modal").modal('hide');
            if (response.status === 'success') {
                $day_table.row("#" + response.data.day.DT_RowId).remove()
                $day_table.row.add(response.data.day).select().draw()    
            }
        });
    });

    let cols = ['date', 'type', 'value'];
    let fields = ['date', 'reading_type', 'value'];
    $reading_table = create_table("#reading_table", cols, fields, 2, {'date': function(date){return date}}, true);

    let reading_editor = new $.fn.dataTable.Editor( {
        ajax: {
            url: "/guardian/me/reading/edit/",
            headers: {'X-CSRFToken': getCookie('csrftoken')},
        },
        table: "#reading_table",
        fields: [  
            {name: "value"},
        ]
    } );

    $reading_table.on( 'click', 'td', function (e) {
        reading_editor.inline( this, {
            onBlur: 'submit'
        } );
    } );

    $('#reading_day_modal').on('hide.bs.modal', function (e) {
        $("#reading_modal_infinity").addClass('hide');
        $("#reading_modal_alerts").children().remove();
    })

    $("#select_reading_date").on('click', function(){
        $("#reading_modal_infinity").removeClass('hide');
        add_alert($("#reading_modal_alerts"), 'warning', 'All readings made for that date. Feel free to select another big boy')
        let selected_date = $("#new_readings_date").val();
        $("#save_new_readings").attr({date: selected_date})
        readings_left(selected_date, function(response){
            let choices = [];
            response.data.readings.forEach(function(reading, index){
                choices.push({text: reading, id: reading});
            });

            if (choices.length >= 0) {
                $("#new_reading_select").select2({
                    data: choices,
                    allowClear: true,
                    multiple: true,
                    closeOnSelect: false,
                    //not sure this is working
                    scrollAfterSelect: true,
                    placeholder: "Select readings"});
            }
            $("#new_reading_select").trigger('change');
            $new_reading_table.rows().remove().draw();
            $("#reading_day_modal").modal('hide');
            $("#reading_day_modal_record").modal('show');
        });


    });

    let rCols = ['reading', 'value']
    $new_reading_table = create_table("#new_reading_table", rCols, rCols, 2, {}, false);

    let new_reading_editor = new $.fn.dataTable.Editor( {
        ajax: function ( method, url, d, successCallback, errorCallback ) {
            var output = { data: [] };
            debugger;
            if ( d.action === 'edit' ) {
                var key = Object.keys(d.data)[0];
                var editedRow = d.data[Object.keys(d.data)[0]];
                editedRow.DT_RowId = key;
                editedRow.id = key;
                editedRow.reading = key;
                output.data.push(editedRow);
             }
  
         successCallback(output);
        },

        table: "#new_reading_table",
        fields: [  
            {name: "value"},
        ]
    } );

    $new_reading_table.on( 'click', 'td', function (e) {
        new_reading_editor.inline( this, {
            onBlur: 'submit'
        } );
    } );

    $("#add_new_reading_button").on('click', function(){
        let additions = [];
        $("#new_reading_select").val().forEach(function(item, index){
            if (!$new_reading_table.rows("#"+item).any()) {
                additions.push({'DT_RowId': item, reading: item, value: 0});
            }
        });
        $new_reading_table.rows.add(additions).draw();

    });

    $("#save_new_readings").on('click', function(){
        let readings = []    
        $.each($new_reading_table.rows().data(), function(key, value){
            readings.push(value);
        });
        save_readings($(this).attr('date'), JSON.stringify(readings), function(response){
            add_alerts($("#reading_alerts"), response.messages);
            if (response.status === 'success') {
                $reading_table.rows.add(response.data.readings).draw();                
            }
            $("#reading_waiting").addClass('hide');
            console.log(response);
        });
        $("#reading_waiting").removeClass('hide');
        $("#reading_day_modal_record").modal('hide');
    });

    $("#save_workout").on('click', function(){
        $("#workout_waiting").removeClass('hide');
        $("#workout_modal").modal('hide');
        save_workout(JSON.stringify($("#workout_form").serializeArray()), function(response){
            add_alerts($("#workout_alerts"), response.messages);
            $workout_table.rows("#" + response.data.removed_primary_key).remove()
            if (response.status === 'success') {
                $workout_table.rows("#" + response.data.workout.primary_key).remove()
                $workout_table.row.add(response.data.workout).draw();
            }
            $("#workout_waiting").addClass('hide');
        });
    });

    $("#new_workout_button").on('click', function(){
        new_workout();
        $("#workout_modal").modal('show');
    });

    $("#workout_table").on("dblclick", "tbody tr", function(){
        var data = $workout_table.row( this ).data();
        set_workout_form(data);
        $("#workout_modal").modal('show');
    });

    $("#delete_selected").on('click', function(){
        let pk = $workout_table.row({selected: true}).data().primary_key;
        $("#confirm_delete_description").text("Are you sure you want to delete selected workout: " + pk + " ?");
        $("#confirm_delete_button").attr({primary_key: pk, model: "Workout"})
        $("#confirm_delete").modal('show');    
    });

    $("#confirm_delete_button").on('click', function(){
        $("#confirm_delete").modal('hide');
        switch ($(this).attr('model')) {
            case "Workout":
                delete_workout($(this).attr('primary_key'), function(response){
                    add_alerts($("#workout_alerts"), response.messages);
                    if (response.status === 'success') {
                        $workout_table.row("#" + response.data.primary_key).remove().draw();
                    }
                });
                break;
            case "Reading":
                delete_reading($(this).attr('primary_key'), function(response){
                    add_alerts($("#reading_alerts"), response.messages);
                    if (response.status === 'success') {
                        $reading_table.row("#" + response.data.primary_key).remove().draw();
                    }
                });
                break;
    
            }
    });


    $("#delete_selected_reading").on('click', function(){
        let pk = $reading_table.row({selected: true}).data().primary_key;
        $("#confirm_delete_description").text("Are you sure you want to delete selected reading: " + pk + " ?");
        $("#confirm_delete_button").attr({primary_key: pk, model: "Reading"})
        $("#confirm_delete").modal('show');    
    });

    $("#rpe, #seconds").on('change', update_rpe_tss);

});

function populate_days(days){
    if ($day_table) {
        $day_table.rows().remove();
        $day_table.rows.add(days).draw();
    } else {
        let cols = ['date', 'day_type', 'comments'];
        $day_table = create_table("#day_table", cols, cols, 2, {'date': function(date){return date}}, true);
        $day_table.rows().remove();
        $day_table.rows.add(days).draw();
    }
    $("#day_waiting").addClass('hide');
}

function populate_readings(readings){
    $reading_table.rows().remove();
    $reading_table.rows.add(readings).draw();
    $("#reading_waiting").addClass('hide');
}

function populate_workouts(workouts){
    if ($workout_table) {
        $workout_table.rows().remove();
        $workout_table.rows.add(workouts).draw()
    }else {
        let cols = ['date', "#", 'activity', 'type', 'equipment', 'duration', 'km', 'ascent', 'rpe', 'tss', 'tss_method', 'watts', 'heart_rate', 'kj', 'cadence', 'reps', 'keywords'];
        let fields = ['date', 'workout_number', 'activity', 'activity_type', 'equipment', 'seconds', 'km', 'ascent_metres', 'rpe', 'tss', 'tss_method', 'watts', 'heart_rate', 'kj', 'cadence', 'reps', 'keywords'];
        let render_dict = {
            'workout_number': function(number){return ""+number},
            'seconds': time_from_seconds,
            'date': function(date){return date}}
        $workout_table = create_table("#workout_table", cols, fields, 1, render_dict, true);
        $workout_table.rows().remove();
        $workout_table.rows.add(workouts).draw();
    }
    $("#workout_waiting").addClass('hide');
}

function new_workout() {
    let today = new Date();
    set_workout_form({
        primary_key: "",
        date: today.toLocaleDateString('en-CA'),
        workout_number: "",
        activity: "Swim",
        activity_type: "Squad",
        equipment: "",
        seconds: 3600,
        km: 0.0,
        rpe: 5,
        tss: 0,
        tss_method: "PacePower",
        kj: 0,
        ascent_metres: 0,
        cadence: 0,
        watts: 0,
        watts_estimated: true,
        is_race: false,
        is_brick: false,
        reps: 0,
        keywords: "",
        comments: ""
    });
}

function set_workout_form(workout_dict) {
    console.log(workout_dict);
    for (var key in workout_dict) {
        set_workout_form_field(key, workout_dict[key]);
    }
    update_rpe_tss();
}

function set_workout_form_field(field, value) {
    switch (field){
        case 'seconds':
            $("#" + field).val(time_from_seconds(value));
            break;
        case "primary_key":
        case "workout_number":
            $("#" + field).val(value);
            break;
        case "activity":
        case "activity_type":
        case "equipment":
        case "tss_method":
            $("#" + field).val(value).trigger('change');
            break;
        case 'is_race':
        case 'is_brick':
        case 'watts_estimated':
            $("#" + field).prop('checked', value == 1);
            break;
        case 'date':
            $("#workout_date").val(value);
            break;
        case 'comments':
            $("#workout_comments").val(value);
            break;
        default:
            $("#" + field).val(value);
        }
 }

 function update_rpe_tss() {
     rpe = parseFloat($('#rpe').val());
     duration = seconds_from_time($('#seconds').val());
     tss = (100 / 49) * rpe * rpe * duration / 3600.0
     $("#rpe_tss").text(tss);
 }