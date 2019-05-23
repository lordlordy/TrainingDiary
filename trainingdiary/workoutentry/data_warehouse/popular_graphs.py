import datetime
from .data_warehouse import DataWarehouse

dw = DataWarehouse.instance()

today = datetime.datetime.now().date()
year_start = datetime.datetime(year=today.year, month=1, day=1).date()
year_end = datetime.datetime(year=today.year, month=12, day=31).date()
max_date = dw.max_date()
min_date = dw.min_date()

TSB = {
        'number_of_plots': 4,
        'colour_map': '57',
        'background': 'aliceblue',
        'graph_display_type': 'Single',
        'from': str(today - datetime.timedelta(days=365)),
        'to': str(today),
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
    }

POPULAR_GRAPHS = {'TSB': TSB}

c = TSB.copy()
c['activity_array'] = ['Swim', 'Swim', 'Swim', 'Swim']
POPULAR_GRAPHS['TSB-Swim'] = c
c = TSB.copy()
c['activity_array'] = ['Bike', 'Bike', 'Bike', 'Bike']
POPULAR_GRAPHS['TSB-Bike'] = c
c = TSB.copy()
c['activity_array'] = ['Run', 'Run', 'Run', 'Run']
POPULAR_GRAPHS['TSB-Run'] = c
c = TSB.copy()
c['activity_array'] = ['Gym', 'Gym', 'Gym', 'Gym']
POPULAR_GRAPHS['TSB-Gym'] = c
c = TSB.copy()
c['activity_array'] = ['Walk', 'Walk', 'Walk', 'Walk']
POPULAR_GRAPHS['TSB-Walk'] = c
c = TSB.copy()
c['activity_array'] = ['Other', 'Other', 'Other', 'Other']
POPULAR_GRAPHS['TSB-Other'] = c

POPULAR_GRAPHS['YTD-km'] = {
        'number_of_plots': 3,
        'colour_map': '35',
        'background': 'black',
        'graph_display_type': 'Single',
        'from': str(year_start),
        'to': str(year_end),
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
    }

equipment = dw.equipment()
axes = ['Primary' for e in equipment]
axes[0] = 'Secondary'

POPULAR_GRAPHS['LTD-Bike-Miles'] = {
        'number_of_plots': len(equipment),
        'colour_map': '52',
        'background': 'antiquewhite',
        'graph_display_type': 'Split',
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
    }

POPULAR_GRAPHS['Scatter-kg-%'] = {
        'number_of_plots': 2,
        'colour_map': '63',
        'background': 'aliceblue',
        'graph_display_type': 'Single',
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
    }

POPULAR_GRAPHS['Physiological'] = {
        'number_of_plots': 9,
        'colour_map': '35',
        'background': 'black',
        'graph_display_type': 'Split',
        'from': str(today - datetime.timedelta(days=365)),
        'to': str(today),
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
    }

POPULAR_GRAPHS['Sleep Impact'] = {
        'number_of_plots': 16,
        'colour_map': '50',
        'background': 'darkgrey',
        'graph_display_type': 'Split',
        'from': str(today - datetime.timedelta(days=365)),
        'to': str(today),
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
    }

c = POPULAR_GRAPHS['Sleep Impact'].copy()
c['graph_type_array'] = ['Point', 'Line'] + ['Scatter' for _ in range(14)]
c['colour_map'] = '57'
c['background'] = 'lightgoldenrodyellow'
POPULAR_GRAPHS['Sleep Impact Scatter'] = c

c = POPULAR_GRAPHS['Sleep Impact'].copy()
c['graph_type_array'] = ['Point', 'Line'] + ['Scatter-Hist' for _ in range(14)]
c['colour_map'] = '57'
c['background'] = 'lightgoldenrodyellow'
POPULAR_GRAPHS['Sleep Impact Scatter Hist'] = c
