var $reading_table;
var $workouts_table;
var $activity_select;
var $activityType_select;
var $equipment_select;
var $tssMethod_select;

$(document).ready(function () {

    $activity_select = refresh_list('activity', $("#activity"), "Select activity");
    $activityType_select = refresh_list('activityType', $("#activityType"), "Select activity type");
    $equipment_select = refresh_list('equipment', $("#equipment"), "Select equipment");
    $tssMethod_select = refresh_list('tssMethod', $("#tssMethod"), "Select method");

    const today = new Date();
    let three_days_ago = new Date();
    three_days_ago.setDate(three_days_ago.getDate() - 3);
    $("#days_from, #readings_from, #workouts_from").val(three_days_ago.toLocaleDateString('en-CA'));
    $("#days_to, #readings_to, #workouts_to").val(today.toLocaleDateString('en-CA'));

    $("#date_select").on('blur', function(){
        console.log($(this).val());
        data_for_date($(this).val(), function(response){
            console.log(response);
            populate_for_day(response.data.Day);
        });
    });


});

function populate_for_day(day){
    if ($reading_table) {
        $reading_table.rows().remove();
        $reading_table.rows.add(day.Readings).draw();
    } else {
        let cols = ['type', 'value'];
        $reading_table = create_table("#readings_table", cols, cols, 2, {});
        $reading_table.rows().remove();
        $reading_table.rows.add(day.Readings).draw();
    }
    if ($workouts_table) {
        $workouts_table.rows().remove();
        $workouts_table.rows.add(day.Workouts).draw()
    }else {
        let cols = ['activity', 'duration', 'km', 'rpe', 'tss'];
        let fields = ['activity', 'seconds', 'km', 'rpe', 'tss'];
        let render_dict = {'seconds': time_from_seconds}
        $workouts_table = create_table("#workouts_table", cols, fields, 1, render_dict);
        wire_workout_table();
        $workouts_table.rows().remove();
        $workouts_table.rows.add(day.Workouts).draw();
    }
}

function wire_workout_table() {
    $workouts_table.on('click', 'tbody tr', function (event) {
        const data = $workouts_table.row("#" + $(this).attr("id")).data();
        for (const key in data) {
            set_form(key, data[key])
          }
    });
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