var $table1;
var $table2;

$(document).ready(function () {

    $("#tss_infinity, #duration_infinity, #km_infinity, #bike_infinity").removeClass('hide');

    refresh_list('years', false, $("#year1"), "Select year", function(response){$("#year1").val('2021').trigger('change')});
    refresh_list('period', false, $("#period1"), "Select period", function(response){$("#period1").val('W-Sun').trigger('change')});
    refresh_list('years', false, $("#year2"), "Select year", function(response){$("#year2").val('2020').trigger('change')});
    refresh_list('period', false, $("#period2"), "Select period", function(response){$("#period2").val('W-Sun').trigger('change')});

    var cols = ["date", "All hours", "Swim km", "Bike km", "Run km"];
    $table1 = create_table("#table1", cols, cols, 1, {'date': function(d){return d;}}, false);
    $table2 = create_table("#table2", cols, cols, 1, {'date': function(d){return d;}}, false);


    $("#refresh1").on('click', function(){
        year_summary($("#year1").val(), $("#period1").val(), function(response){
            add_alerts($("#year1_alerts"), response.messages);
            $table1.rows().remove();
            $table1.rows.add(response.data.time_series).draw();
            set_title2();
        });
    });

    $("#refresh2").on('click', function(){
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