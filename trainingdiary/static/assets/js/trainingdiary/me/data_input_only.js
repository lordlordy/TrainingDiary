var $day_table;
var $reading_table;
var $workout_table;
var $activity_select;
var $activityType_select;
var $equipment_select;
var $tssMethod_select;
var $dayType_select;

$(document).ready(function () {

    $activity_select = refresh_list('activity', $("#activity"), "Select activity");
    $activityType_select = refresh_list('activityType', $("#activityType"), "Select activity type");
    $equipment_select = refresh_list('equipment', $("#equipment"), "Select equipment");
    $tssMethod_select = refresh_list('tssMethod', $("#tssMethod"), "Select method");
    $dayType_select = refresh_list('dayType', $("#day_type_select"), "Select type");

    const today = new Date();
    let from_date = new Date();
    from_date.setDate(from_date.getDate() - 14);
    let from_str = from_date.toLocaleDateString('en-CA');
    let to_str = today.toLocaleDateString('en-CA');
    $("#day_from, #reading_from, #workout_from").val(from_str);
    $("#day_to, #reading_to, #workout_to, #new_readings_date").val(to_str);

    $("#day_waiting, #reading_waiting, #workout_waiting").removeClass('hide');
    data_for_between('Day', from_str, to_str, function(response){populate_days(response.data.instances)});
    data_for_between('Reading', from_str, to_str, function(response){populate_readings(response.data.instances)});
    data_for_between('Workout', from_str, to_str, function(response){populate_workouts(response.data.instances)});

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
        // let form_data = JSON.stringify($("#day_form").serializeArray());
        save_day($("#date").val(), $("#day_type_select").val(), $("#comments").val(), function(response){
            add_alerts($("#day_alerts"), response.messages);
            $("#day_modal").modal('hide');
            if (response.status === 'success') {
                $day_table.row("#" + response.data.day.DT_RowId).remove()
                $day_table.row.add(response.data.day).select().draw()    
            }
            console.log(response);
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
        readings_left($("#new_readings_date").val(), function(response){
            console.log(response);
        });
    });

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
    console.log(workouts)
    if ($workout_table) {
        $workout_table.rows().remove();
        $workout_table.rows.add(workouts).draw()
    }else {
        let cols = ['date', 'activity', 'type', 'equipment', 'duration', 'km', 'ascent', 'rpe', 'tss', 'tss_method', 'watts', 'heart_rate', 'kj', 'cadence', 'reps', 'keywords'];
        let fields = ['date', 'activity', 'activity_type', 'equipment', 'seconds', 'km', 'ascent_metres', 'rpe', 'tss', 'tss_method', 'watts', 'heart_rate', 'kj', 'cadence', 'reps', 'keywords'];
        let render_dict = {
            'seconds': time_from_seconds,
            'date': function(date){return date}}
        $workout_table = create_table("#workout_table", cols, fields, 1, render_dict, true);
        $workout_table.rows().remove();
        $workout_table.rows.add(workouts).draw();
    }
    $("#workout_waiting").addClass('hide');
}

function set_form(field, value) {
    switch (field){
        case 'seconds':
            $("#" + field).val(time_from_seconds(value));
            break;
        case "DT_RowId":
            $("#" + field).text(value);
            break;
        case "activity":
        case "activityType":
        case "equipment":
        case "tssMethod":
            $("#" + field).val(value).trigger('change');
            break;
        case 'isRace':
        case 'isBrick':
        case 'wattsEstimated':
            $("#" + field).prop('checked', value == 1);
            break;
        default:
             $("#" + field).val(value);
     }
 }