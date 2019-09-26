import datetime
import dateutil


def create_popular_graphs(data_warehouse):

    max_date = data_warehouse.max_date()
    min_date = data_warehouse.min_date()
    start_date = str(dateutil.parser.parse(max_date).date() - datetime.timedelta(days=365))
    end_date = max_date

    tsb = {
            'number_of_plots': 4,
            'colour_map': '57',
            'background': 'aliceblue',
            'graph_display_type': 'Single',
            'share_axis': 'None',
            'from': start_date,
            'to': end_date,
            'period_array': ['Day', 'Day', 'Day', 'Day'],
            'aggregation_array': ['Sum', 'Sum', 'Sum', 'Sum'],
            'activity_array': ['All', 'All', 'All', 'All'],
            'activity_type_array': ['All', 'All', 'All', 'All'],
            'equipment_array': ['All', 'All', 'All', 'All'],
            'measure_array': ['ctl', 'atl', 'tsb', 'tss'],
            'to_date_array': ['No', 'No', 'No', 'No'],
            'rolling_array': ['No', 'No', 'No', 'No'],
            'rolling_periods_array': ['1', '1', '1', '1'],
            'rolling_aggregation_array': ['Sum', 'Sum', 'Sum', 'Sum'],
            'day_of_week_array': ['All', 'All', 'All', 'All'],
            'month_array': ['All', 'All', 'All', 'All'],
            'day_type_array': ['All', 'All', 'All', 'All'],
            'graph_type_array': ['Line', 'Line', 'Fill', 'Point'],
            'axis_array': ['Primary', 'Primary', 'Primary', 'Secondary'],
            'size_array': ['3', '3', '3', '6'],
            'recorded_only_array': ['Yes', 'Yes', 'Yes', 'Yes'],
            'plot_zeroes_array': ['Yes', 'Yes', 'Yes', 'No'],
    }

    popular_graphs = {'tsb': tsb}

    c = tsb.copy()
    c['activity_array'] = ['Swim', 'Swim', 'Swim', 'Swim']
    popular_graphs['tsb-Swim'] = c
    c = tsb.copy()
    c['activity_array'] = ['Bike', 'Bike', 'Bike', 'Bike']
    popular_graphs['tsb-Bike'] = c
    c = tsb.copy()
    c['activity_array'] = ['Run', 'Run', 'Run', 'Run']
    popular_graphs['tsb-Run'] = c
    c = tsb.copy()
    c['activity_array'] = ['Gym', 'Gym', 'Gym', 'Gym']
    popular_graphs['tsb-Gym'] = c
    c = tsb.copy()
    c['activity_array'] = ['Walk', 'Walk', 'Walk', 'Walk']
    popular_graphs['tsb-Walk'] = c
    c = tsb.copy()
    c['activity_array'] = ['Other', 'Other', 'Other', 'Other']
    popular_graphs['tsb-Other'] = c

    r = range(3)
    popular_graphs['resting hr'] = {
        'number_of_plots': 3,
        'colour_map': '56',
        'background': 'dodgerblue',
        'graph_display_type': 'Single',
        'share_axis': 'None',
        'from': start_date,
        'to': end_date,
        'period_array': ['Day' for _ in r],
        'aggregation_array': ['Sum' for _ in r],
        'activity_array': ['All' for _ in r],
        'activity_type_array': ['All' for _ in r],
        'equipment_array': ['All' for _ in r],
        'measure_array': ['resting_hr', 'resting_hr', 'resting_hr'],
        'to_date_array': ['No' for _ in r],
        'rolling_array': ['No', 'Yes', 'Yes'],
        'rolling_periods_array': [1, 7, 31],
        'rolling_aggregation_array': ['Mean' for _ in r],
        'day_of_week_array': ['All' for _ in r],
        'month_array': ['All' for _ in r],
        'day_type_array': ['All' for _ in r],
        'graph_type_array': ['Point', 'Line', 'Line', 'Line', 'Line'],
        'axis_array': ['Primary' for _ in r],
        'size_array': ['6', '3', '1'],
        'recorded_only_array': ['Yes', 'No', 'No'],
        'plot_zeroes_array': ['No' for _ in r],
       }

    r = range(6)
    hrv = {'number_of_plots': 6,
           'colour_map': '56',
           'background': 'dodgerblue',
           'graph_display_type': 'Single',
           'share_axis': 'None',
           'from': start_date,
           'to': end_date,
           'period_array': ['Day' for _ in r],
           'aggregation_array': ['Sum' for _ in r],
           'activity_array': ['All' for _ in r],
           'activity_type_array': ['All' for _ in r],
           'equipment_array': ['All' for _ in r],
           'measure_array': ['sdnn', 'sdnn_off', 'sdnn_easy', 'sdnn_mean', 'sdnn_hard', 'sdnn'],
           'to_date_array': ['No' for _ in r],
           'rolling_array': ['No', 'No', 'No', 'No', 'No', 'Yes'],
           'rolling_periods_array': [1, 1, 1, 1, 1, 7],
           'rolling_aggregation_array': ['Sum', 'Sum', 'Sum', 'Sum', 'Sum', 'Mean'],
           'day_of_week_array': ['All' for _ in r],
           'month_array': ['All' for _ in r],
           'day_type_array': ['All' for _ in r],
           'graph_type_array': ['Point', 'Line', 'Line', 'Line', 'Line', 'Line'],
           'axis_array': ['Primary' for _ in r],
           'size_array': ['8', '3', '3', '3', '3', '1'],
           'recorded_only_array': ['Yes', 'No', 'No', 'No', 'No', 'No'],
           'plot_zeroes_array': ['No', 'Yes', 'Yes', 'Yes', 'Yes', 'No'],
           }

    popular_graphs['hrv_SDNN'] = hrv
    c = hrv.copy()
    c['measure_array'] = ['rmssd', 'rmssd_off', 'rmssd_easy', 'rmssd_mean', 'rmssd_hard', 'rmssd']
    popular_graphs['hrv_rMSSD'] = c


    popular_graphs['YTD-km'] = {
            'number_of_plots': 3,
            'colour_map': '35',
            'background': 'black',
            'graph_display_type': 'Single',
            'share_axis': 'None',
            'from': start_date,
            'to': end_date,
            'period_array': ['Y-Dec', 'Y-Dec', 'Y-Dec'],
            'aggregation_array': ['Sum', 'Sum', 'Sum'],
            'activity_array': ['Swim', 'Bike', 'Run'],
            'activity_type_array': ['All', 'All', 'All'],
            'equipment_array': ['All', 'All', 'All'],
            'measure_array': ['km', 'km', 'km'],
            'to_date_array': ['Yes', 'Yes', 'Yes'],
            'rolling_array': ['No', 'No', 'No'],
            'rolling_periods_array': ['1', '1', '1'],
            'rolling_aggregation_array': ['Sum', 'Sum', 'Sum'],
            'day_of_week_array': ['All', 'All', 'All'],
            'month_array': ['All', 'All', 'All'],
            'day_type_array': ['All', 'All', 'All'],
            'graph_type_array': ['Fill', 'Fill', 'Fill'],
            'axis_array': ['Primary', 'Secondary', 'Primary'],
            'size_array': ['3', '3', '3'],
            'recorded_only_array': ['Yes', 'Yes', 'Yes'],
            'plot_zeroes_array': ['Yes', 'Yes', 'Yes'],
    }

    equipment = data_warehouse.equipment()
    axes = ['Primary' for e in equipment]
    axes[0] = 'Secondary'

    popular_graphs['LTD-Bike-Miles'] = {
            'number_of_plots': len(equipment),
            'colour_map': '52',
            'background': 'antiquewhite',
            'graph_display_type': 'Split',
            'share_axis': 'None',
            'from': min_date,
            'to': max_date,
            'period_array': ['Day' for e in equipment],
            'aggregation_array': ['Sum' for e in equipment],
            'activity_array': ['All' for e in equipment],
            'activity_type_array': ['All' for e in equipment],
            'equipment_array': equipment,
            'measure_array': ['miles' for e in equipment],
            'to_date_array': ['No' for e in equipment],
            'rolling_array': ['Yes' for e in equipment],
            'rolling_periods_array': ['10000' for e in equipment],
            'rolling_aggregation_array': ['Sum' for e in equipment],
            'day_of_week_array': ['All' for e in equipment],
            'month_array': ['All' for e in equipment],
            'day_type_array': ['All' for e in equipment],
            'graph_type_array': ['Line' for e in equipment],
            'axis_array': axes,
            'size_array': ['3' for e in equipment],
            'recorded_only_array': ['Yes' for e in equipment],
            'plot_zeroes_array': ['Yes' for e in equipment],
    }

    popular_graphs['Scatter-kg-%'] = {
            'number_of_plots': 2,
            'colour_map': '63',
            'background': 'aliceblue',
            'graph_display_type': 'Single',
            'share_axis': 'None',
            'from': min_date,
            'to': max_date,
            'period_array': ['Day', 'Day'],
            'aggregation_array': ['Sum', 'Sum'],
            'activity_array': ['All', "All"],
            'activity_type_array': ['All', 'All'],
            'equipment_array': ['All', 'All'],
            'measure_array': ['kg', 'fat_percentage'],
            'to_date_array': ['No', 'No'],
            'rolling_array': ['No', 'No'],
            'rolling_periods_array': ['1', '1'],
            'rolling_aggregation_array': ['Sum', 'Sum'],
            'day_of_week_array': ['All', 'All'],
            'month_array': ['All', 'All'],
            'day_type_array': ['All', 'All'],
            'graph_type_array': ['Scatter-Hist', 'Scatter-Hist'],
            'axis_array': ['Primary', 'Primary'],
            'size_array': ['3', '3'],
            'recorded_only_array': ['Yes', 'Yes'],
            'plot_zeroes_array': ['No', 'No'],
    }

    popular_graphs['Physiological'] = {
            'number_of_plots': 9,
            'colour_map': '35',
            'background': 'black',
            'graph_display_type': 'Split',
            'share_axis': 'None',
            'from': start_date,
            'to': end_date,
            'period_array': ['Day' for i in range(9)],
            'aggregation_array': ['Sum' for i in range(9)],
            'activity_array': ['All' for i in range(9)],
            'activity_type_array': ['All' for i in range(9)],
            'equipment_array': ['All' for i in range(9)],
            'measure_array': ['sleep_hours', 'motivation', 'fatigue', 'kg', 'fat_percentage', 'resting_hr', 'sdnn', 'rmssd', 'hours'],
            'to_date_array': ['No' for i in range(9)],
            'rolling_array': ['Yes' for i in range(9)],
            'rolling_periods_array': ['7' for i in range(9)],
            'rolling_aggregation_array': ['Mean' for i in range(9)],
            'day_of_week_array': ['All' for i in range(9)],
            'month_array': ['All' for i in range(9)],
            'day_type_array': ['All' for i in range(9)],
            'graph_type_array': ['Fill', 'Fill', 'Fill', 'Line', 'Line', 'Line', 'Line', 'Line', 'Fill'],
            'axis_array': ['Primary' for i in range(9)],
            'size_array': ['2' for i in range(9)],
            'recorded_only_array': ['No' for i in range(9)],
            'plot_zeroes_array': ['No' for i in range(9)]
    }


    popular_graphs['Physiological Buckets'] = {
            'number_of_plots': 9,
            'colour_map': '57',
            'background': 'darkgray',
            'graph_display_type': 'Split',
            'share_axis': 'None',
            'from': min_date,
            'to': max_date,
            'period_array': ['Day' for _ in range(9)],
            'aggregation_array': ['Sum' for _ in range(9)],
            'activity_array': ['All' for _ in range(9)],
            'activity_type_array': ['All' for _ in range(9)],
            'equipment_array': ['All' for _ in range(9)],
            'measure_array': ['fatigue', 'motivation', 'sleep_hours', 'kg', 'fat_percentage', 'resting_hr', 'sdnn', 'rmssd', 'hours'],
            'to_date_array': ['No' for _ in range(9)],
            'rolling_array': ['No' for _ in range(9)],
            'rolling_periods_array': ['1' for _ in range(9)],
            'rolling_aggregation_array': ['Sum' for i in range(9)],
            'day_of_week_array': ['All' for _ in range(9)],
            'month_array': ['All' for _ in range(9)],
            'day_type_array': ['All' for _ in range(9)],
            'graph_type_array': ['Histogram'for _ in range(9)],
            'axis_array': ['Primary' for _ in range(9)],
            'size_array': ['10', '10'] + ['20' for _ in range(9)],
            'recorded_only_array': ['No' for i in range(9)],
            'plot_zeroes_array': ['No' for i in range(9)]
    }


    popular_graphs['Swims By Day Buckets'] = {
            'number_of_plots': 7,
            'colour_map': '57',
            'background': 'darkgray',
            'graph_display_type': 'Split',
            'share_axis': 'Both',
            'from': min_date,
            'to': max_date,
            'period_array': ['Day' for _ in range(7)],
            'aggregation_array': ['Sum' for _ in range(7)],
            'activity_array':  ['Swim' for _ in range(7)],
            'activity_type_array': ['All' for _ in range(7)],
            'equipment_array': ['All' for _ in range(7)],
            'measure_array': ['km' for _ in range(7)],
            'to_date_array': ['No' for _ in range(7)],
            'rolling_array': ['No' for _ in range(7)],
            'rolling_periods_array': ['1' for _ in range(7)],
            'rolling_aggregation_array': ['Sum' for i in range(7)],
            'day_of_week_array': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'month_array': ['All' for _ in range(7)],
            'day_type_array': ['All' for _ in range(7)],
            'graph_type_array': ['Histogram'for _ in range(7)],
            'axis_array': ['Primary' for _ in range(7)],
            'size_array': ['15' for _ in range(7)],
            'recorded_only_array': ['No' for i in range(7)],
            'plot_zeroes_array': ['No' for i in range(7)]
    }


    popular_graphs['Rides By Day Buckets'] = {
            'number_of_plots': 7,
            'colour_map': '57',
            'background': 'darkgray',
            'graph_display_type': 'Split',
            'share_axis': 'Both',
            'from': min_date,
            'to': max_date,
            'period_array': ['Day' for _ in range(7)],
            'aggregation_array': ['Sum' for _ in range(7)],
            'activity_array':  ['Bike' for _ in range(7)],
            'activity_type_array': ['All' for _ in range(7)],
            'equipment_array': ['All' for _ in range(7)],
            'measure_array': ['km' for _ in range(7)],
            'to_date_array': ['No' for _ in range(7)],
            'rolling_array': ['No' for _ in range(7)],
            'rolling_periods_array': ['1' for _ in range(7)],
            'rolling_aggregation_array': ['Sum' for i in range(7)],
            'day_of_week_array': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'month_array': ['All' for _ in range(7)],
            'day_type_array': ['All' for _ in range(7)],
            'graph_type_array': ['Histogram'for _ in range(7)],
            'axis_array': ['Primary' for _ in range(7)],
            'size_array': ['25' for _ in range(7)],
            'recorded_only_array': ['No' for i in range(7)],
            'plot_zeroes_array': ['No' for i in range(7)]
    }

    popular_graphs['Runs By Day Buckets'] = {
            'number_of_plots': 7,
            'colour_map': '57',
            'background': 'darkgray',
            'graph_display_type': 'Split',
            'share_axis': 'Both',
            'from': min_date,
            'to': max_date,
            'period_array': ['Day' for _ in range(7)],
            'aggregation_array': ['Sum' for _ in range(7)],
            'activity_array':  ['Run' for _ in range(7)],
            'activity_type_array': ['All' for _ in range(7)],
            'equipment_array': ['All' for _ in range(7)],
            'measure_array': ['km' for _ in range(7)],
            'to_date_array': ['No' for _ in range(7)],
            'rolling_array': ['No' for _ in range(7)],
            'rolling_periods_array': ['1' for _ in range(7)],
            'rolling_aggregation_array': ['Sum' for i in range(7)],
            'day_of_week_array': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'month_array': ['All' for _ in range(7)],
            'day_type_array': ['All' for _ in range(7)],
            'graph_type_array': ['Histogram'for _ in range(7)],
            'axis_array': ['Primary' for _ in range(7)],
            'size_array': ['20' for _ in range(7)],
            'recorded_only_array': ['No' for i in range(7)],
            'plot_zeroes_array': ['No' for i in range(7)]
    }

    popular_graphs['Swims By Month Buckets'] = {
            'number_of_plots': 12,
            'colour_map': '57',
            'background': 'darkgray',
            'graph_display_type': 'Split',
            'share_axis': 'Both',
            'from': min_date,
            'to': max_date,
            'period_array': ['Day' for _ in range(12)],
            'aggregation_array': ['Sum' for _ in range(12)],
            'activity_array':  ['Swim' for _ in range(12)],
            'activity_type_array': ['All' for _ in range(12)],
            'equipment_array': ['All' for _ in range(12)],
            'measure_array': ['km' for _ in range(12)],
            'to_date_array': ['No' for _ in range(12)],
            'rolling_array': ['No' for _ in range(12)],
            'rolling_periods_array': ['1' for _ in range(12)],
            'rolling_aggregation_array': ['Sum' for _ in range(12)],
            'day_of_week_array': ['All' for _ in range(12)],
            'month_array': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'day_type_array': ['All' for _ in range(12)],
            'graph_type_array': ['Histogram'for _ in range(12)],
            'axis_array': ['Primary' for _ in range(12)],
            'size_array': ['15' for _ in range(12)],
            'recorded_only_array': ['No' for i in range(12)],
            'plot_zeroes_array': ['No' for i in range(12)]
    }


    popular_graphs['Bikes By Month Buckets'] = {
            'number_of_plots': 12,
            'colour_map': '57',
            'background': 'darkgray',
            'graph_display_type': 'Split',
            'share_axis': 'Both',
            'from': min_date,
            'to': max_date,
            'period_array': ['Day' for _ in range(12)],
            'aggregation_array': ['Sum' for _ in range(12)],
            'activity_array':  ['Bike' for _ in range(12)],
            'activity_type_array': ['All' for _ in range(12)],
            'equipment_array': ['All' for _ in range(12)],
            'measure_array': ['km' for _ in range(12)],
            'to_date_array': ['No' for _ in range(12)],
            'rolling_array': ['No' for _ in range(12)],
            'rolling_periods_array': ['1' for _ in range(12)],
            'rolling_aggregation_array': ['Sum' for _ in range(12)],
            'day_of_week_array': ['All' for _ in range(12)],
            'month_array': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'day_type_array': ['All' for _ in range(12)],
            'graph_type_array': ['Histogram'for _ in range(12)],
            'axis_array': ['Primary' for _ in range(12)],
            'size_array': ['20' for _ in range(12)],
            'recorded_only_array': ['No' for i in range(12)],
            'plot_zeroes_array': ['No' for i in range(12)]
    }

    popular_graphs['Runs By Month Buckets'] = {
            'number_of_plots': 12,
            'colour_map': '57',
            'background': 'darkgray',
            'graph_display_type': 'Split',
            'share_axis': 'Both',
            'from': min_date,
            'to': max_date,
            'period_array': ['Day' for _ in range(12)],
            'aggregation_array': ['Sum' for _ in range(12)],
            'activity_array':  ['Run' for _ in range(12)],
            'activity_type_array': ['All' for _ in range(12)],
            'equipment_array': ['All' for _ in range(12)],
            'measure_array': ['km' for _ in range(12)],
            'to_date_array': ['No' for _ in range(12)],
            'rolling_array': ['No' for _ in range(12)],
            'rolling_periods_array': ['1' for _ in range(12)],
            'rolling_aggregation_array': ['Sum' for _ in range(12)],
            'day_of_week_array': ['All' for _ in range(12)],
            'month_array': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'day_type_array': ['All' for _ in range(12)],
            'graph_type_array': ['Histogram'for _ in range(12)],
            'axis_array': ['Primary' for _ in range(12)],
            'size_array': ['20' for _ in range(12)],
            'recorded_only_array': ['No' for i in range(12)],
            'plot_zeroes_array': ['No' for i in range(12)]
    }

    popular_graphs['Activity Day Buckets'] = {
            'number_of_plots': 9,
            'colour_map': '57',
            'background': 'darkgray',
            'graph_display_type': 'Split',
            'share_axis': 'None',
            'from': min_date,
            'to': max_date,
            'period_array': ['Day' for _ in range(9)],
            'aggregation_array': ['Sum' for _ in range(9)],
            'activity_array':  ['Swim', 'Bike', 'Run', 'All', 'All', 'Bike', 'Bike', 'All', 'All'],
            'activity_type_array': ['All' for _ in range(9)],
            'equipment_array': ['All' for _ in range(9)],
            'measure_array': ['km', 'km', 'km', 'hours', 'tss', 'watts', 'ascent_metres', 'ctl', 'atl'],
            'to_date_array': ['No' for _ in range(9)],
            'rolling_array': ['No' for _ in range(9)],
            'rolling_periods_array': ['1' for _ in range(9)],
            'rolling_aggregation_array': ['Sum' for i in range(9)],
            'day_of_week_array': ['All' for _ in range(9)],
            'month_array': ['All' for _ in range(9)],
            'day_type_array': ['All' for _ in range(9)],
            'graph_type_array': ['Histogram'for _ in range(9)],
            'axis_array': ['Primary' for _ in range(9)],
            'size_array': ['20' for _ in range(9)],
            'recorded_only_array': ['No' for i in range(9)],
            'plot_zeroes_array': ['No' for i in range(9)]
    }


    popular_graphs['Activity Week Buckets'] = {
            'number_of_plots': 9,
            'colour_map': '57',
            'background': 'darkgray',
            'graph_display_type': 'Split',
            'share_axis': 'None',
            'from': min_date,
            'to': max_date,
            'period_array': ['W-Sun' for _ in range(9)],
            'aggregation_array': ['Sum', 'Sum', 'Sum', 'Sum', 'Sum', 'Mean', 'Sum', 'Mean', 'Mean'],
            'activity_array':  ['Swim', 'Bike', 'Run', 'All', 'All', 'Bike', 'Bike', 'All', 'All'],
            'activity_type_array': ['All' for _ in range(9)],
            'equipment_array': ['All' for _ in range(9)],
            'measure_array': ['km', 'km', 'km', 'hours', 'tss', 'watts', 'ascent_metres', 'ctl', 'atl'],
            'to_date_array': ['No' for _ in range(9)],
            'rolling_array': ['No' for _ in range(9)],
            'rolling_periods_array': ['1' for _ in range(9)],
            'rolling_aggregation_array': ['Sum' for i in range(9)],
            'day_of_week_array': ['All' for _ in range(9)],
            'month_array': ['All' for _ in range(9)],
            'day_type_array': ['All' for _ in range(9)],
            'graph_type_array': ['Histogram'for _ in range(9)],
            'axis_array': ['Primary' for _ in range(9)],
            'size_array': ['20' for _ in range(9)],
            'recorded_only_array': ['No' for i in range(9)],
            'plot_zeroes_array': ['No' for i in range(9)]
    }


    popular_graphs['Activity Month Buckets'] = {
            'number_of_plots': 9,
            'colour_map': '57',
            'background': 'darkgray',
            'graph_display_type': 'Split',
            'share_axis': 'None',
            'from': min_date,
            'to': max_date,
            'period_array': ['Month' for _ in range(9)],
            'aggregation_array': ['Sum', 'Sum', 'Sum', 'Sum', 'Sum', 'Mean', 'Sum', 'Mean', 'Mean'],
            'activity_array':  ['Swim', 'Bike', 'Run', 'All', 'All', 'Bike', 'Bike', 'All', 'All'],
            'activity_type_array': ['All' for _ in range(9)],
            'equipment_array': ['All' for _ in range(9)],
            'measure_array': ['km', 'km', 'km', 'hours', 'tss', 'watts', 'ascent_metres', 'ctl', 'atl'],
            'to_date_array': ['No' for _ in range(9)],
            'rolling_array': ['No' for _ in range(9)],
            'rolling_periods_array': ['1' for _ in range(9)],
            'rolling_aggregation_array': ['Sum' for i in range(9)],
            'day_of_week_array': ['All' for _ in range(9)],
            'month_array': ['All' for _ in range(9)],
            'day_type_array': ['All' for _ in range(9)],
            'graph_type_array': ['Histogram'for _ in range(9)],
            'axis_array': ['Primary' for _ in range(9)],
            'size_array': ['20' for _ in range(9)],
            'recorded_only_array': ['No' for i in range(9)],
            'plot_zeroes_array': ['No' for i in range(9)]
    }

    popular_graphs['Sleep Impact'] = {
            'number_of_plots': 16,
            'colour_map': '50',
            'background': 'darkgrey',
            'graph_display_type': 'Split',
            'share_axis': 'None',
            'from': start_date,
            'to': end_date,
            'period_array': ['Day' for i in range(16)],
            'aggregation_array': ['Sum' for i in range(16)],
            'activity_array': ['All' for i in range(16)],
            'activity_type_array': ['All' for i in range(16)],
            'equipment_array': ['All' for i in range(16)],
            'measure_array': ['sleep_hours', 'sleep_hours',
                              'sleep_hours', 'fatigue',
                              'sleep_hours', 'motivation',
                              'sleep_hours', 'kg',
                              'sleep_hours', 'fat_percentage',
                              'sleep_hours', 'resting_hr',
                              'sleep_hours', 'sdnn',
                              'sleep_hours', 'rmssd'],
            'to_date_array': ['No' for i in range(16)],
            'rolling_array': ['No', 'Yes'] + ['No' for i in range(14)],
            'rolling_periods_array': ['1', '10'] + ['1' for i in range(14)],
            'rolling_aggregation_array': ['Mean' for i in range(16)],
            'day_of_week_array': ['All' for i in range(16)],
            'month_array': ['All' for i in range(16)],
            'day_type_array': ['All' for i in range(16)],
            'graph_type_array': ['Point', 'Line'] + ['Heatmap' for i in range(14)],
            'axis_array': ['Primary' for i in range(16)],
            'size_array': ['2', '2'] + ['15' for i in range(14)],
            'recorded_only_array': ['No' for i in range(16)],
            'plot_zeroes_array': ['No' for i in range(16)]
        }

    c = popular_graphs['Sleep Impact'].copy()
    c['graph_type_array'] = ['Point', 'Line'] + ['Scatter' for _ in range(14)]
    c['colour_map'] = '57'
    c['background'] = 'lightgoldenrodyellow'
    popular_graphs['Sleep Impact Scatter'] = c

    c = popular_graphs['Sleep Impact'].copy()
    c['graph_type_array'] = ['Point', 'Line'] + ['Scatter-Hist' for _ in range(14)]
    c['colour_map'] = '57'
    c['background'] = 'lightgoldenrodyellow'
    popular_graphs['Sleep Impact Scatter Hist'] = c

    return popular_graphs