var $dataset_table;
var datasets = new Array();
var scales = new Object();
var chart;
var selected_dataset;

$(document).ready(function () {

    create_series_form("#time_series_form");

    var cols = ["DT_RowId", "label", "type", "borderColor", "backgroundColor", "fill", "pointRadius", "pointHoverRadius", "showLine", "xAxisID", "yAxisID"];
    $dataset_table = create_table("#dataset_table", cols, cols, 0, {}, true);
    
    $("#calculate_time_series").on('click', function(){
        $("#series_waiting").removeClass('hide');
        time_series(JSON.stringify($("#time_series_form").serializeArray()), function(response){
            add_alerts($("#series_alerts"), response.messages);
            response.data.time_series.datasets.forEach(function(dataset, i) { 
                datasets.push(dataset); 
            });
            for (const [key, value] of Object.entries(response.data.time_series.scales)) {
                if (key in scales) {
                    if (key.charAt(0) === 'x') {
                        // no labels currently on x axis so no need to combine anything
                    } else {
                        debugger;
                        // add this text to existing text
                        var currentText = scales[key].title.text;
                        scales[key].title.text = currentText + " " + value.title.text;
                    }
                } else {
                    scales[key] = value;
                }
            }
            chart = plot_chart("chart", "chart-container", datasets, scales, response.data.chart_title)
            $dataset_table.rows.add(response.data.time_series.datasets).draw();
            $("#series_waiting").addClass('hide');
        });
    });

    $("#dataset_table").on("click", "tbody tr", function(){
        var data = $dataset_table.row( this ).data();
        update_table_for_selected_row(data);
    });

    $("#update_dataset").on('click', update_chart_from_inputs);

});

function update_table_for_selected_row(dataset) {
    selected_dataset = dataset;
    $("#DT_RowId").val(dataset.DT_RowId);
    $("#label").val(dataset.label);
    $("#chart_type").val(dataset.type);
    $("#borderColor").val(dataset.borderColor);
    $("#backgroundColor").val(dataset.backgroundColor);
    $("#fill").val(dataset.fill);
    $("#pointRadius").val(dataset.pointRadius);
    $("#pointHoverRadius").val(dataset.pointHoverRadius);
    $("#showLine").val(dataset.showLine);
    $("#yAxisID").val(dataset.yAxisID);
}

function update_chart_from_inputs() {
    selected_dataset.label = $("#label").val();
    selected_dataset.type = $("#chart_type").val();
    selected_dataset.borderColor = $("#borderColor").val();
    selected_dataset.backgroundColor = $("#backgroundColor").val();
    selected_dataset.fill = $("#fill").val() == 'true';
    selected_dataset.pointRadius = $("#pointRadius").val();
    selected_dataset.pointHoverRadius = $("#pointHoverRadius").val();
    selected_dataset.showLine = $("#showLine").val() === 'true';
    selected_dataset.yAxisID = $("#yAxisID").val();
    $dataset_table.rows().invalidate().draw();
    chart.update();
}

