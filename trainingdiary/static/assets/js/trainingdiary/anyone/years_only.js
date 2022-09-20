var $table1;
var $table2;
var period1;
var period2;

$(document).ready(function () {

    $("#tss_infinity, #duration_infinity, #km_infinity, #bike_infinity").removeClass('hide');

    refresh_list('years', false, $("#year1"), "Select year", function(response){$("#year1").val('2022').trigger('change')});
    refresh_list('period', false, $("#period1"), "Select period", function(response){$("#period1").val('W-Sun').trigger('change')});
    refresh_list('years', false, $("#year2"), "Select year", function(response){$("#year2").val('2021').trigger('change')});
    refresh_list('period', false, $("#period2"), "Select period", function(response){$("#period2").val('W-Sun').trigger('change')});

    var headings = ["date", "Hours", "Swim", "Bike", "Run", "Press Ups"];
    var data_keys = ["date", "All hours", "Swim km", "Bike km", "Run km", "Gym PressUp reps"];
    $table1 = create_table("#table1", headings, data_keys, 1, {'date': date_converter1}, false);
    $table2 = create_table("#table2", headings, data_keys, 1, {'date': date_converter2}, false);


    $("#refresh1").on('click', function(){
        period1 = $("#period1").val().charAt(0);
        year_summary($("#year1").val(), $("#period1").val(), function(response){
            console.log(response)
            add_alerts($("#year1_alerts"), response.messages);
            $table1.rows().remove();
            $table1.rows.add(response.data.time_series).draw();
            set_title2();
        });
    });

    $("#refresh2").on('click', function(){
        period2 = $("#period2").val().charAt(0);
        year_summary($("#year2").val(), $("#period2").val(), function(response){
            add_alerts($("#year2_alerts"), response.messages);
            $table2.rows().remove();
            $table2.rows.add(response.data.time_series).draw();
            set_title2();
        });
    });

});

function set_title1() {
    $("#title1").text($("#year1").val() + " : " + $("#period1").val());
}

function set_title2() {
    $("#title2").text($("#year2").val() + " : " + $("#period2").val());
}

function date_converter1(data, type, row, meta ) {
    return convert_date(period1, data, type, meta);
}

function date_converter2(data, type, row, meta ) {
    return convert_date(period2, data, type, meta);
}

function convert_date(period, data, type, meta) {
    
    if (type === 'display') {
        let month = parseInt(data.substring(5,7)) - 1;
        switch (period) {
            case 'W':
                return "Wk-" + (meta.row + 1) + " " + data.substring(8,10) + "-" + SHORT_MONTHS[month];
                break;
            case 'Q':
                return "Q-" + (meta.row + 1) + " " + SHORT_MONTHS[month];
                break;
            case 'M':
                return LONG_MONTHS[month]
                break;
            default:
                return data;
        }
    }
    return data;
}