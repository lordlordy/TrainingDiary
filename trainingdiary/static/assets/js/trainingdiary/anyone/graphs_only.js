$(document).ready(function () {

    create_series_form("#eddington_form");

    $("#plot_series").on('click', function(){
        $("#series_waiting").removeClass('hide');
        time_series(JSON.stringify($("#series_form").serializeArray()), function(response){
            add_alerts($("#series_alerts"), response.messages);
            plot_chart("chart", "chart-container", response.data.time_series, response.data.chart_title)
            $("#series_waiting").addClass('hide');
        });
    });

});
