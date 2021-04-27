var $bike_summary_table;
var $reading_table;
var $workouts_table;
var $km_table;
var $duration_table;
var $tss_table;
var $activity_select;
var $activityType_select;
var $equipment_select;
var $tssMethod_select;

$(document).ready(function () {

    $("#tss_infinity, #duration_infinity, #km_infinity, #bike_infinity").removeClass('hide');

    $activity_select = refresh_list('activity', $("#activity"), "Select activity");
    $activityType_select = refresh_list('activityType', $("#activityType"), "Select activity type");
    $equipment_select = refresh_list('equipment', $("#equipment"), "Select equipment");
    $tssMethod_select = refresh_list('tssMethod', $("#tssMethod"), "Select method");

    bike_summary(function(response){
        $bike_summary_table = create_table("#bike_summary_table", response.data.years, response.data.years, 0, {});
        $bike_summary_table.rows.add(response.data.bikes).draw();
    })

    training_summary(function(response){
        var cols = ["year", "Total", "Swim", "Bike", "Run", "Walk"];
        let fields = ["name", "Total.km", "Swim.km", "Bike.km", "Run.km", "Walk.km"];
        $km_table = create_table("#km_table", cols, fields, 0, {"name": $.fn.dataTable.render.number( '', '.', 0 )});
        $km_table.rows.add(response.data.years).draw();
        cols.push('Gym');
        cols.push('Other');
        let render_dict = {
            "name": $.fn.dataTable.render.number( '', '.', 0 ),
            "Total.seconds": time_from_seconds, 
            "Swim.seconds": time_from_seconds, 
            "Bike.seconds": time_from_seconds, 
            "Run.seconds": time_from_seconds, 
            "Walk.seconds": time_from_seconds, 
            "Gym.seconds": time_from_seconds, 
            "Other.seconds": time_from_seconds}
        let seconds_fields = ["name", "Total.seconds", "Swim.seconds", "Bike.seconds", "Run.seconds", "Walk.seconds", "Gym.seconds", "Other.seconds"];
        $duration_table = create_table("#duration_table", cols, seconds_fields, 0, render_dict);
        $duration_table.rows.add(response.data.years).draw();

        let tss_fields = ["name", "Total.tss", "Swim.tss", "Bike.tss", "Run.tss", "Walk.tss", "Gym.tss", "Other.tss"];
        $tss_table = create_table("#tss_table", cols, tss_fields, 0, render_dict);
        $tss_table.rows.add(response.data.years).draw();

        $tss_table.on('select', function(e, dt, type, indexes){ create_chart($tss_table);});
        $duration_table.on('select', function(e, dt, type, indexes){ create_chart($duration_table);});
        $km_table.on('select', function(e, dt, type, indexes){ create_chart($km_table);});
        $bike_summary_table.on('select', function(e, dt, type, indexes){ create_chart($bike_summary_table);});

        $("#tss_infinity, #duration_infinity, #km_infinity, #bike_infinity").addClass('hide');

    });

    $("#date_select").on('blur', function(){
        console.log($(this).val());
        data_for_date($(this).val(), function(response){
            console.log(response);
            populate_for_day(response.data.Day);
        });
    });

    $("#workout_save").on("click", function(){
        console.log("save");
        var workout_data = $("#workout_form").serializeArray();
        console.log(JSON.stringify(workout_data));
    });
});

function create_chart($table) {
    var column = 'Total';
    var row = '2021';
    // currently only single selection 
    $table.cells({selected: true}).every(function(rowIdx, colIdx, tablecounter, cellcounter){
        column = $table.column(colIdx).header().innerText;
        row = $table.row(rowIdx).data().name;
    });
    switch ($table){
        case $tss_table:
            $duration_table.cell('.selected').deselect().draw();
            $km_table.cell('.selected').deselect().draw();
            $bike_summary_table.cell('.selected').deselect().draw();
            graph = 'tss';
            break;
        case $duration_table:
            $tss_table.cell('.selected').deselect().draw();
            $km_table.cell('.selected').deselect().draw();
            $bike_summary_table.cell('.selected').deselect().draw();
            graph = 'duration';
            break;
        case $km_table:
            $tss_table.cell('.selected').deselect().draw();
            $duration_table.cell('.selected').deselect().draw();
            $bike_summary_table.cell('.selected').deselect().draw();
            graph = 'km';
            break;
        case $bike_summary_table:
            $tss_table.cell('.selected').deselect().draw();
            $duration_table.cell('.selected').deselect().draw();
            $km_table.cell('.selected').deselect().draw();
            graph = 'bike';
            break;
    }
    let $waiting = $("#" + graph + "_infinity");
    $waiting.removeClass('hide');
    graph_data(graph, row, column, function(response){
        console.log(response);
        plot_chart(graph + "-chart", graph + "-chart-container", response.data.time_series, response.data.chart_title)
        $waiting.addClass('hide');
    }); 
}

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