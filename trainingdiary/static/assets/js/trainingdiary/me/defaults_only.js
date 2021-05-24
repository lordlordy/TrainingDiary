var $chart_defaults_table;

$(document).ready(function(){
    create_series_form("#defaults_form");
    createYesNoSelect($("#fill, #showLine, #draw_grid_lines"), 'yes');


    var cols = ['unique_key', 'label', 'chart_type', 'borderColor', 'backgroundColor', 'fill', 'pointRadius', 
    'pointHoverRadius', 'showLine', 'position', 'number', 'scale_type', 'draw_grid_lines']

    $chart_defaults_table = create_table("#chart_defaults_table", cols, cols, 0, {}, true);


    graph_defaults(function(response){
        console.log(response);
        add_alerts($("#defaults_alerts"), response.messages);
        if (response.status === 'success') {
            $chart_defaults_table.rows.add(response.data.defaults).draw();
        }
    });

    $("#add_update").on('click', function(){
        save_graph_defaults(JSON.stringify($("#defaults_form").serializeArray()), function(response){
            console.log(response)
            add_alerts($("#defaults_alerts"), response.messages);
            
            if (response.status === 'success') {
                $chart_defaults_table.rows("#" + response.data.defaults_added[0].unique_key).remove()
                $chart_defaults_table.row.add(response.data.defaults_added[0]).draw();
            }
        });
    });

    $("#chart_defaults_table").on("click", "tbody tr", function(){
        var data = $chart_defaults_table.row( this ).data();
        set_defaults_form(data);
    });

    $("#delete_selected").on('click', function(){
        let key = $chart_defaults_table.row({selected: true}).data().DT_RowId;
        delete_graph_defaults(key, function(response){
            console.log(response)
            add_alerts($("#defaults_alerts"), response.messages);
            if (response.status === 'success') {
                $chart_defaults_table.row("#" + response.data.deleted_unique_key).remove().draw();
            }
        })

    });

    $("#new_definition").on('click', function(){
        $("#unique_key").val("").trigger('change');
    });

});

function set_defaults_form(defaults_dict) {
    console.log(defaults_dict);
    for (var key in defaults_dict) {
        set_defaults_form_field(key, defaults_dict[key]);
    }
}

function set_defaults_form_field(field, value) {
    switch (field){

        case "draw_grid_lines":
        case "fill":
        case "showLine":
            $("#" + field).val(value ? 'yes' : 'no').trigger('change');
            break;
        default:
            $("#" + field).val(value).trigger('change');
    }
 }
