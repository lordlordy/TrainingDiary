var $bike_summary_table;
var $km_table;
var $duration_table;
var $tss_table;
var $reading_table;

$(document).ready(function () {

    $("#tss_infinity, #duration_infinity, #km_infinity, #bike_infinity, #reading_infinity").removeClass('hide');

    create_series_form("#time_series_form")

    bike_summary(function(response){
        $bike_summary_table = create_table("#bike_summary_table", response.data.years, response.data.years, 0, {}, false);
        $bike_summary_table.rows.add(response.data.bikes).draw();
        $bike_summary_table.on('select', function(e, dt, type, indexes){ create_chart($bike_summary_table);});
        $("#bike_infinity").addClass('hide');
    })

    training_summary(function(response){
        var cols = ["year", "Total", "Swim", "Bike", "Run", "Walk"];
        let fields = ["name", "Total.km", "Swim.km", "Bike.km", "Run.km", "Walk.km"];
        $km_table = create_table("#km_table", cols, fields, 0, {"name": $.fn.dataTable.render.number( '', '.', 0 )}, false);
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
        $duration_table = create_table("#duration_table", cols, seconds_fields, 0, render_dict, false);
        $duration_table.rows.add(response.data.years).draw();

        let tss_fields = ["name", "Total.tss", "Swim.tss", "Bike.tss", "Run.tss", "Walk.tss", "Gym.tss", "Other.tss"];
        $tss_table = create_table("#tss_table", cols, tss_fields, 0, render_dict, false);
        $tss_table.rows.add(response.data.years).draw();

        $tss_table.on('select', function(e, dt, type, indexes){ create_chart($tss_table);});
        $duration_table.on('select', function(e, dt, type, indexes){ create_chart($duration_table);});
        $km_table.on('select', function(e, dt, type, indexes){ create_chart($km_table);});

        $("#tss_infinity, #duration_infinity, #km_infinity").addClass('hide');

    });

    reading_summary(function(response){
        var cols = ["year", "kg", "lbs", "fatPercentage", "motivation", "fatigue", "sleep", "sleepQualityScore", "readiness", "restingHR", "SDNN", "rMSSD"];
        let fields = ["date", "All kg", "All lbs", "All fatPercentage", "All motivation", "All fatigue", "All sleep", "All sleepQualityScore", "All readiness", "All restingHR", "All SDNN", "All rMSSD"];
        $reading_table = create_table("#reading_summary_table", cols, fields, 2, {"date": $.fn.dataTable.render.number( '', '.', 0 )}, false);
        $reading_table.rows.add(response.data.time_series).draw();    
        $reading_table.on('select', function(e, dt, type, indexes){ create_chart($reading_table);});

        $("#reading_infinity").addClass('hide');

    });

    $(".card-header").on('dblclick', function(){
        console.log('dblclick');
        $(this).siblings().toggleClass('hide');
    });

    $("#calculate_time_series").on('click', function(){
        $("#adhoc_infinity").removeClass('hide');
        time_series(JSON.stringify($("#time_series_form").serializeArray()), function(response){
            add_alerts($("#time_series_alerts"), response.messages);
            plot_chart("adhoc-chart", "adhoc-chart-container", response.data.time_series.datasets, response.data.time_series.scales, response.data.chart_title)
            $("#adhoc_infinity").addClass('hide');
        });
    });

    $(".card-body").addClass('hide')

});

function create_chart($table) {
    var activity = 'Total';
    var year = '2021';
    // currently only single selection 
    $table.cells({selected: true}).every(function(rowIdx, colIdx, tablecounter, cellcounter){
        column = $table.column(colIdx).header().innerText;
        row = $table.row(rowIdx).data().name;
        activity = column;
        year = row;
    });
    switch ($table){
        case $tss_table:
            $duration_table.cell('.selected').deselect().draw();
            $km_table.cell('.selected').deselect().draw();
            $bike_summary_table.cell('.selected').deselect().draw();
            $reading_table.cell('.selected').deselect().draw();
            graph = 'tss';
            break;
        case $duration_table:
            $tss_table.cell('.selected').deselect().draw();
            $km_table.cell('.selected').deselect().draw();
            $bike_summary_table.cell('.selected').deselect().draw();
            $reading_table.cell('.selected').deselect().draw();
            graph = 'duration';
            break;
        case $km_table:
            $tss_table.cell('.selected').deselect().draw();
            $duration_table.cell('.selected').deselect().draw();
            $bike_summary_table.cell('.selected').deselect().draw();
            $reading_table.cell('.selected').deselect().draw();
            graph = 'km';
            break;
        case $reading_table:
            $tss_table.cell('.selected').deselect().draw();
            $duration_table.cell('.selected').deselect().draw();
            $bike_summary_table.cell('.selected').deselect().draw();
            $km_table.cell('.selected').deselect().draw();
            graph = 'reading';
            break;
        case $bike_summary_table:
            $tss_table.cell('.selected').deselect().draw();
            $duration_table.cell('.selected').deselect().draw();
            $km_table.cell('.selected').deselect().draw();
            $reading_table.cell('.selected').deselect().draw();
            graph = 'bike';
            // year is on column so need to switch
            year = column;
            activity = row;
            break;
    }
    let $waiting = $("#" + graph + "_infinity");
    $waiting.removeClass('hide');
    graph_data(graph, year, activity, function(response){
        plot_chart(graph + "-chart", graph + "-chart-container", response.data.time_series.datasets, response.data.time_series.scales, response.data.chart_title)
        $waiting.addClass('hide');
    }); 
}
