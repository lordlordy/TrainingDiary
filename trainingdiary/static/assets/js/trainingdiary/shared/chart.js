function plot_chart(chart_id, chart_container_id, time_series_dict, chart_title) {

    $('#' + chart_id).remove();
    $('#' + chart_container_id).append('<canvas id="' + chart_id + '"></canvas>');
    var chart = $('#' + chart_id)[0].getContext("2d");
    var chart_config = {
        data: {
            datasets: time_series_dict.datasets
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    font: {
                        size: 20
                    },
                    text: chart_title
                }
            },
            tooltips: {
                position: 'nearest',
                mode: 'point',
                intersect: false,
                displayColors: false,
            },
            scales: time_series_dict.scales
        }
    };

    console.log(chart_config)

    return new Chart(chart, chart_config);
}