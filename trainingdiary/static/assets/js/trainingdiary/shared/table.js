
function create_table(table_id, headings, data_keys, decimal_places, render_dict, can_search) {
    let $table_header = $(table_id).find("thead tr");
    headings.forEach(function(heading, index){
        let $column = $("<th>").text(heading);
        $table_header.append($column);
    });
    let cols = [];
    data_keys.forEach(function(data_key, index){
        if (data_key in render_dict){
            cols.push(
                {
                    data: data_key,
                    render: render_dict[data_key],
                }
            );    
        } else {
            cols.push(
                {
                    data: data_key,
                    render: $.fn.dataTable.render.number( ',', '.', decimal_places )
                }
            );    
        }
    });
    let $table = $(table_id).DataTable({
        "order": [[ 0, "desc" ]],
        select: {
            style: 'single',
            items: can_search ? 'row' : 'cell',
        },
        info: can_search,
        searching: can_search,
        paging: can_search,
        columns: cols
    });
    return $table;
}

