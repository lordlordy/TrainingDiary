var $bike_summary_table;
var $km_table;
var $duration_table;
var $tss_table;

$(document).ready(function () {

    $("#tss_infinity, #duration_infinity, #km_infinity, #bike_infinity").removeClass('hide');

    create_series_form("#eddington_form")

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

    $(".card-header").on('dblclick', function(){
        console.log('dblclick');
        $(this).siblings().toggleClass('hide');
    });

    $("#calculate_eddington_number").on('click', function(){
        $("#eddington_infinity").removeClass('hide');
        time_series(JSON.stringify($("#eddington_form").serializeArray()), function(response){
            add_alerts($("#eddington_alerts"), response.messages);
            plot_chart("eddington-chart", "eddington-chart-container", response.data.time_series, response.data.chart_title)
            $("#eddington_infinity").addClass('hide');
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
            // year is on column so need to switch
            year = column;
            activity = row;
            break;
    }
    let $waiting = $("#" + graph + "_infinity");
    $waiting.removeClass('hide');
    graph_data(graph, year, activity, function(response){
        plot_chart(graph + "-chart", graph + "-chart-container", response.data.time_series, response.data.chart_title)
        $waiting.addClass('hide');
    }); 
}
