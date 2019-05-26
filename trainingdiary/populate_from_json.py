import json
import datetime
from datetime import date
from dateutil import parser
import sqlite3
import numpy as np
import pandas as pd
import math

JSON = 'json'
DB_COL = 'db_col'
TYPE = 'type'
FACTOR = 'factor'
REAL = 'REAL'
INTEGER = 'INTEGER'
BOOLEAN = 'BOOLEAN'
DEFAULT = 'DEFAULT'
AGGREGATION_METHOD = 'AggMethod'
MAPPER = 'Mapper'
SUM = 'Sum'
MEAN = 'Mean'
DAY = 'Day'
WEEK = 'Week'
MONTH = 'Month'

MILES_PER_KM = 0.621371

workout_map = [{JSON: 'km', DB_COL: 'km', TYPE: REAL, FACTOR: 1.0, DEFAULT: 0.0, AGGREGATION_METHOD: SUM},
               {JSON: 'km', DB_COL: 'miles', TYPE: REAL, FACTOR: MILES_PER_KM, DEFAULT: 0.0, AGGREGATION_METHOD: SUM},
               {JSON: 'tss', DB_COL: 'tss', TYPE: INTEGER, FACTOR: 1.0, DEFAULT: 0, AGGREGATION_METHOD: SUM},
               {JSON: 'rpe', DB_COL: 'rpe', TYPE: REAL, FACTOR: 1.0, DEFAULT: 0.0, AGGREGATION_METHOD: MEAN},
               {JSON: 'hr', DB_COL: 'hr', TYPE: INTEGER, FACTOR: 1.0, DEFAULT: 0, AGGREGATION_METHOD: MEAN},
               {JSON: 'watts', DB_COL: 'watts', TYPE: INTEGER, FACTOR: 1.0, DEFAULT: 0, AGGREGATION_METHOD: MEAN},
               {JSON: 'seconds', DB_COL: 'seconds', TYPE: INTEGER, FACTOR: 1.0, DEFAULT: 0, AGGREGATION_METHOD: SUM},
               {JSON: 'seconds', DB_COL: 'minutes', TYPE: INTEGER, FACTOR: 1.0 / 60.0, DEFAULT: 0, AGGREGATION_METHOD: SUM},
               {JSON: 'seconds', DB_COL: 'hours', TYPE: REAL, FACTOR: 1.0 / (60.0 * 60.0), DEFAULT: 0.0, AGGREGATION_METHOD: SUM},
               {JSON: 'ascentMetres', DB_COL: 'ascent_metres', TYPE: INTEGER, FACTOR: 1.0, DEFAULT: 0, AGGREGATION_METHOD: SUM},
               {JSON: 'ascentMetres', DB_COL: 'ascent_feet', TYPE: INTEGER, FACTOR: 3.28084, DEFAULT: 0, AGGREGATION_METHOD: SUM},
               {JSON: 'kj', DB_COL: 'kj', TYPE: INTEGER, FACTOR: 1.0, DEFAULT: 0, AGGREGATION_METHOD: SUM},
               {JSON: 'reps', DB_COL: 'reps', TYPE: INTEGER, FACTOR: 1.0, DEFAULT: 0, AGGREGATION_METHOD: SUM},
               {JSON: 'isRace', DB_COL: 'is_race', TYPE: BOOLEAN, FACTOR: 1.0, DEFAULT: 0, AGGREGATION_METHOD: SUM},
               {JSON: 'brick', DB_COL: 'brick', TYPE: BOOLEAN, FACTOR: 1.0, DEFAULT: 0, AGGREGATION_METHOD: SUM},
               {JSON: 'wattsEstimated', DB_COL: 'watts_estimated', TYPE: BOOLEAN, FACTOR: 1.0, DEFAULT: 0, AGGREGATION_METHOD: SUM},
               {JSON: 'cadence', DB_COL: 'cadence', TYPE: INTEGER, FACTOR: 1.0, DEFAULT: 0, AGGREGATION_METHOD: MEAN},
               {JSON: 'rpe_tss', DB_COL: 'rpe_tss', TYPE: REAL, DEFAULT: 0.0, AGGREGATION_METHOD: SUM, MAPPER: 'rpe_tss_mapper'},
               {JSON: 'mph', DB_COL: 'mph', TYPE: REAL, DEFAULT: 0.0, AGGREGATION_METHOD: MEAN, MAPPER: 'mph_mapper'},
               {JSON: 'kph', DB_COL: 'kph', TYPE: REAL, DEFAULT: 0.0, AGGREGATION_METHOD: MEAN, MAPPER: 'kph_mapper'}]

workout_col_names = ','.join([m[DB_COL] for m in workout_map])
workout_zeroes = ','.join(['0' for _ in workout_map])
workout_col_creation = ','.join(f'{m[DB_COL]} {m[TYPE]} DEFAULT {m[DEFAULT]}' for m in workout_map)

day_map = [{JSON: 'fatigue', DB_COL: 'fatigue', TYPE: REAL, FACTOR: 1.0, DEFAULT: 0, AGGREGATION_METHOD: MEAN},
           {JSON: 'motivation', DB_COL: 'motivation', TYPE: REAL, FACTOR: 1.0, DEFAULT: 0, AGGREGATION_METHOD: MEAN},
           {JSON: 'sleep', DB_COL: 'sleep_seconds', TYPE: INTEGER, FACTOR: 60.0 * 60.0, DEFAULT: 0, AGGREGATION_METHOD: SUM},
           {JSON: 'sleep', DB_COL: 'sleep_minutes', TYPE: INTEGER, FACTOR: 60.0, DEFAULT: 0, AGGREGATION_METHOD: SUM},
           {JSON: 'sleep', DB_COL: 'sleep_hours', TYPE: REAL, FACTOR: 1.0, DEFAULT: 0.0, AGGREGATION_METHOD: SUM},
           {JSON: 'type', DB_COL: 'type', TYPE: 'VARCHAR(32)', FACTOR: 1.0, DEFAULT: "Normal"},
           {JSON: 'sleepQuality', DB_COL: 'sleep_quality', TYPE: 'VARCHAR(32)', FACTOR: 1.0, DEFAULT: 'Average'}]

day_col_names = ','.join(m[DB_COL] for m in day_map)
day_col_creation = ','.join(f"{m[DB_COL]} {m[TYPE]} DEFAULT {m[DEFAULT]}" for m in day_map)

calculated_map = [{DB_COL: 'ctl', TYPE: REAL, DEFAULT: 0.0, AGGREGATION_METHOD: MEAN},
                  {DB_COL: 'atl', TYPE: REAL, DEFAULT: 0.0, AGGREGATION_METHOD: MEAN},
                  {DB_COL: 'tsb', TYPE: REAL, DEFAULT: 0.0, AGGREGATION_METHOD: MEAN},
                  {DB_COL: 'rpe_ctl', TYPE: REAL, DEFAULT: 0.0, AGGREGATION_METHOD: MEAN},
                  {DB_COL: 'rpe_atl', TYPE: REAL, DEFAULT: 0.0, AGGREGATION_METHOD: MEAN},
                  {DB_COL: 'rpe_tsb', TYPE: REAL, DEFAULT: 0.0, AGGREGATION_METHOD: MEAN},
                  {DB_COL: 'monotony', TYPE: REAL, DEFAULT: 0.0, AGGREGATION_METHOD: MEAN},
                  {DB_COL: 'strain', TYPE: REAL, DEFAULT: 0.0, AGGREGATION_METHOD: MEAN},
                  {DB_COL: 'rpe_monotony', TYPE: REAL, DEFAULT: 0.0, AGGREGATION_METHOD: MEAN},
                  {DB_COL: 'rpe_strain', TYPE: REAL, DEFAULT: 0.0, AGGREGATION_METHOD: MEAN},
                  ]

calculated_col_creation = ','.join(f"{m[DB_COL]} {m[TYPE]} DEFAULT {m[DEFAULT]}" for m in calculated_map)

physiological_map = [
    {DB_COL: 'kg', TYPE: REAL, DEFAULT: 0.0},
    {DB_COL: 'lbs', TYPE: REAL, DEFAULT: 0.0},
    {DB_COL: 'fat_percentage', TYPE: REAL, DEFAULT: 0.0},
    {DB_COL: 'resting_hr', TYPE: INTEGER, DEFAULT: 0.0},
    {DB_COL: 'sdnn', TYPE: REAL, DEFAULT: 0.0},
    {DB_COL: 'rmssd', TYPE: REAL, DEFAULT: 0.0},
    {DB_COL: 'kg_recorded', TYPE: BOOLEAN, DEFAULT: 0},
    {DB_COL: 'lbs_recorded', TYPE: BOOLEAN, DEFAULT: 0},
    {DB_COL: 'fat_percentage_recorded', TYPE: BOOLEAN, DEFAULT: 0},
    {DB_COL: 'resting_hr_recorded', TYPE: BOOLEAN, DEFAULT: 0},
    {DB_COL: 'sdnn_recorded', TYPE: BOOLEAN, DEFAULT: 0},
    {DB_COL: 'rmssd_recorded', TYPE: BOOLEAN, DEFAULT: 0},
]

physiological_col_creation = ','.join(f"{m[DB_COL]} {m[TYPE]} DEFAULT {m[DEFAULT]}" for m in physiological_map)

ACTIVITY = 'activityString'
ACTIVITY_TYPE = 'activityTypeString'
EQUIPMENT = 'equipmentName'
NOT_SET = 'Not Set'

CTL_DECAY_DAYS = 42
CTL_IMPACT_DAYS = 42
ATL_DECAY_DAYS = 7
ATL_IMPACT_DAYS = 7
CTL_DECAY = np.exp(-1 / CTL_DECAY_DAYS)
CTL_IMPACT = 1 - np.exp(-1 / CTL_IMPACT_DAYS)
ATL_DECAY = np.exp(-1 / ATL_DECAY_DAYS)
ATL_IMPACT = 1 - np.exp(-1 / ATL_IMPACT_DAYS)
table_names = set()

DB_NAME = 'training_data_warehouse.sqlite3'

def populate(print_progress=False):

    st = datetime.datetime.now()
    conn = sqlite3.connect(DB_NAME)
    f = open('TrainingDiary.json')
    data = json.load(f)
    days = data['days']

    for d in days:
        date_time = parser.parse(d['iso8061DateString'])
        d_date = date(date_time.year, date_time.month, date_time.day)
        d_values = value_string_for_sql(d, day_map)

        if 'workouts' in d:
            save_workouts(conn, d_date, d['type'], d_values, d['workouts'])
        else:
            execute_day_sql(conn, d_date, d['type'], day_col_names, d_values,
                            activity='All', activity_type='All', equipment_name='All')
        # fill in gaps
        for t in table_names:
            if not day_exists(d_date, t, conn):
                execute_day_sql(conn, d_date, d['type'], day_col_names, d_values, table_name=t)
        if print_progress:
            print(f'{datetime.datetime.now() - st} {d_date}',end='\r')

    conn.commit()
    conn.close()
    print(f'{datetime.datetime.now() - st} {d_date}')


def populate_kg_fat_percent(print_progress=False):

    st = datetime.datetime.now()
    conn = sqlite3.connect(DB_NAME)
    f = open('TrainingDiary.json')
    data = json.load(f)

    min_date = conn.cursor().execute('SELECT min(date) FROM Day_All_All_All').fetchall()[0][0]
    max_date = conn.cursor().execute('SELECT max(date) FROM Day_All_All_All').fetchall()[0][0]

    kg_dates = []
    kg_array = []
    fat_dates = []
    fat_percent = []
    if 'weights' in data:
        for d in data['weights']:
            date_time = parser.parse(d['iso8061DateString'])
            d_date = date(date_time.year, date_time.month, date_time.day)
            kg = round(float(d['kg']), 1)
            fatpercent = round(float(d['fatPercent']), 1)
            if kg > 0:
                kg_dates.append(d_date)
                kg_array.append(kg)
            if fat > 0:
                fat_dates.append(d_date)
                fat_percent.append(fatpercent)
            if print_progress:
                print(f'{datetime.datetime.now() - st} {d_date}', end='\r')

    print(f'{datetime.datetime.now() - st} {d_date}           ')

    kg_series = pd.Series(kg_array, index=pd.to_datetime(kg_dates))
    kg_series = kg_series.reindex(index=pd.date_range(min_date, max_date)).interpolate(method='linear')
    fat_series = pd.Series(fat_percent, index=pd.to_datetime(fat_dates))
    fat_series = fat_series.reindex(index=pd.date_range(min_date, max_date)).interpolate(method='linear')

    t_list = table_list(conn)
    t_total = len(t_list)
    t_count = 0
    for table in t_list:
        t_count += 1
        for d, value in kg_series.iteritems():
            if math.isnan(value):
                value = 0
            lbs = round(value * 2.20462, 1)
            sql_str = f'UPDATE {table} SET kg={round(value,1)}, lbs={lbs} WHERE date="{str(d.date())}"'
            conn.cursor().execute(sql_str)
            if print_progress:
                print(f'{t_count/t_total:.2%} {datetime.datetime.now() - st} {table}', '               ', end='\r')
        for d, value in fat_series.iteritems():
            if math.isnan(value):
                value = 0
            sql_str = f'UPDATE {table} SET fat_percentage={round(value,1)} WHERE date="{str(d.date())}"'
            conn.cursor().execute(sql_str)
            if print_progress:
                print(f'{t_count/t_total:.2%} {datetime.datetime.now() - st} {table}', '               ', end='\r')

    print(f'100% {datetime.datetime.now() - st} {table}                   ')

    print('setting flag on recorded ...')
    kg_date_str = ', '.join([f"'{str(d)}'" for d in kg_dates])
    fat_date_str = ', '.join([f"'{str(d)}'" for d in fat_dates])
    t_count = 0
    for table in t_list:
        t_count += 1
        sql_str = f'UPDATE {table} SET kg_recorded=1, lbs_recorded=1 WHERE date IN ({kg_date_str})'
        conn.cursor().execute(sql_str)
        if print_progress:
            print(f'{t_count/t_total:.2%} {datetime.datetime.now() - st} {table}', '               ', end='\r')
        sql_str = f'UPDATE {table} SET fat_percentage_recorded=1 WHERE date IN ({fat_date_str})'
        conn.cursor().execute(sql_str)
        if print_progress:
            print(f'{t_count/t_total:.2%} {datetime.datetime.now() - st} {table}', '               ', end='\r')

    conn.commit()
    conn.close()
    print(f'100% {datetime.datetime.now() - st} {table}                   ')


def populate_hr_sdnn_rmssd(print_progress=False):

    st = datetime.datetime.now()
    conn = sqlite3.connect(DB_NAME)
    f = open('TrainingDiary.json')
    data = json.load(f)

    min_date = conn.cursor().execute('SELECT min(date) FROM Day_All_All_All').fetchall()[0][0]
    max_date = conn.cursor().execute('SELECT max(date) FROM Day_All_All_All').fetchall()[0][0]

    hr_dates = []
    hr_array = []
    sdnn_dates = []
    sdnn_array = []
    rmssd_dates = []
    rmssd_array = []
    if 'physiologicals' in data:
        for d in data['physiologicals']:
            date_time = parser.parse(d['iso8061DateString'])
            d_date = date(date_time.year, date_time.month, date_time.day)
            hr = sdnn = rmssd = 0
            if d['restingHR'] is not None:
                hr = int(d['restingHR'])
            if d['restingSDNN'] is not None:
                sdnn = round(float(d['restingSDNN']), 1)
            if d['restingRMSSD'] is not None:
                rmssd = round(float(d['restingRMSSD']), 1)
            if hr > 0:
                hr_dates.append(d_date)
                hr_array.append(hr)
            if sdnn > 0:
                sdnn_dates.append(d_date)
                sdnn_array.append(sdnn)
            if rmssd > 0:
                rmssd_dates.append(d_date)
                rmssd_array.append(sdnn)
            if print_progress:
                print(f'{datetime.datetime.now() - st} {d_date}', end='\r')

    print(f'{datetime.datetime.now() - st} {d_date}')

    hr_series = pd.Series(hr_array, index=pd.to_datetime(hr_dates))
    hr_series = hr_series.reindex(index=pd.date_range(min_date, max_date)).interpolate(method='linear')
    sdnn_series = pd.Series(sdnn_array, index=pd.to_datetime(sdnn_dates))
    sdnn_series = sdnn_series.reindex(index=pd.date_range(min_date, max_date)).interpolate(method='linear')
    rmssd_series = pd.Series(sdnn_array, index=pd.to_datetime(rmssd_dates))
    rmssd_series = rmssd_series.reindex(index=pd.date_range(min_date, max_date)).interpolate(method='linear')

    t_list = table_list(conn)
    t_total = len(t_list)
    t_count = 0
    for table in t_list:
        t_count += 1
        for d, value in hr_series.iteritems():
            if value is None or math.isnan(value):
                value = 0
            sql_str = f'UPDATE {table} SET resting_hr={value} WHERE date="{str(d.date())}"'
            conn.cursor().execute(sql_str)
            if print_progress:
                print(f'{t_count/t_total:.2%} {datetime.datetime.now() - st} {table}', '               ', end='\r')
        for d, value in sdnn_series.iteritems():
            if value is None or math.isnan(value):
                value = 0
            sql_str = f'UPDATE {table} SET sdnn={round(value,1)} WHERE date="{str(d.date())}"'
            conn.cursor().execute(sql_str)
            if print_progress:
                print(f'{t_count/t_total:.2%} {datetime.datetime.now() - st} {table}', '               ', end='\r')
        for d, value in rmssd_series.iteritems():
            if value is None or math.isnan(value):
                value = 0
            sql_str = f'UPDATE {table} SET rmssd={round(value,1)} WHERE date="{str(d.date())}"'
            conn.cursor().execute(sql_str)
            if print_progress:
                print(f'{t_count/t_total:.2%} {datetime.datetime.now() - st} {table}', '               ', end='\r')

    print(f'100% {datetime.datetime.now() - st} {table}', '               ')

    print('setting flag on recorded ...')
    hr_date_str = ', '.join([f"'{str(d)}'" for d in hr_dates])
    sdnn_date_str = ', '.join([f"'{str(d)}'" for d in sdnn_dates])
    rmssd_date_str = ', '.join([f"'{str(d)}'" for d in rmssd_dates])
    t_count = 0
    for table in t_list:
        t_count += 1
        sql_str = f'UPDATE {table} SET resting_hr_recorded=1 WHERE date IN ({hr_date_str})'
        conn.cursor().execute(sql_str)
        if print_progress:
            print(f'{t_count/t_total:.2%} {datetime.datetime.now() - st} {table}', '               ', end='\r')
        sql_str = f'UPDATE {table} SET sdnn_recorded=1 WHERE date IN ({sdnn_date_str})'
        conn.cursor().execute(sql_str)
        if print_progress:
            print(f'{t_count/t_total:.2%} {datetime.datetime.now() - st} {table}', '               ', end='\r')
        sql_str = f'UPDATE {table} SET rmssd_recorded=1 WHERE date IN ({rmssd_date_str})'
        conn.cursor().execute(sql_str)
        if print_progress:
            print(f'{t_count/t_total:.2%} {datetime.datetime.now() - st} {table}', '               ', end='\r')

    conn.commit()
    conn.close()
    print(f'100% {datetime.datetime.now() - st} {table}                   ')


def table_list(conn):
    sql_str = f'SELECT table_name FROM Tables'
    results = conn.cursor().execute(sql_str)
    return [r[0] for r in results]


def calculate_all_tsb(print_progress=False):
    st = datetime.datetime.now()
    conn = sqlite3.connect(DB_NAME)

    t_list = table_list(conn)
    t_total = len(t_list)
    t_count = 0
    for table_name in t_list:
        t_count += 1
        sql_str = f'SELECT id, tss, rpe_tss FROM {table_name} ORDER BY date'
        atl = ctl = rpe_atl = rpe_ctl = 0.0

        results = conn.cursor().execute(sql_str)
        for r in results:
            id = r[0]
            tss = r[1]
            rpe_tss = r[2]
            ctl = tss * CTL_IMPACT + ctl * CTL_DECAY
            atl = tss * ATL_IMPACT + atl * ATL_DECAY
            tsb = ctl - atl
            rpe_ctl = rpe_tss * CTL_IMPACT + rpe_ctl * CTL_DECAY
            rpe_atl = rpe_tss * ATL_IMPACT + rpe_atl * ATL_DECAY
            rpe_tsb = rpe_ctl - rpe_atl
            sql_str = f'''
                UPDATE {table_name} SET 
                ctl={ctl}, atl={atl}, tsb={tsb}, rpe_ctl={rpe_ctl}, rpe_atl={rpe_atl}, rpe_tsb={rpe_tsb} 
                WHERE id={id}'''
            conn.cursor().execute(sql_str)
            if print_progress:
                print(f'{t_count/t_total:.2%} {datetime.datetime.now() - st} {table_name}', '               ', end='\r')

    conn.commit()
    conn.close()
    print(f'100% {datetime.datetime.now() - st} {table_name}', '               ')


def calculate_all_strain(print_progress=False):
    st = datetime.datetime.now()
    conn = sqlite3.connect(DB_NAME)

    t_list = table_list(conn)
    t_total = len(t_list)
    t_count = 0
    for table_name in t_list:
        t_count += 1
        df = pd.read_sql(f'SELECT id, date, tss, rpe_tss from {table_name} ORDER BY date', conn)
        df['tss_stdev'] = df['tss'].rolling(7, min_periods=0).std().clip(lower=0.01)
        df['rpe_tss_stdev'] = df['rpe_tss'].rolling(7, min_periods=0).std().clip(lower=0.01)
        df['monotony'] = df['tss'].rolling(7, min_periods=1).mean() / df['tss_stdev']
        df['strain'] = df['tss'].rolling(7, min_periods=1).sum() * df['monotony']
        df['rpe_monotony'] = df['rpe_tss'].rolling(7, min_periods=1).mean() / df['rpe_tss_stdev']
        df['rpe_strain'] = df['rpe_tss'].rolling(7, min_periods=1).sum() * df['rpe_monotony']
        df.fillna(0, inplace=True)

        for index, row in df.iterrows():
            sql_str = f'''
                UPDATE {table_name} SET
                monotony={row['monotony']}, strain={row['strain']}, 
                rpe_monotony={row['rpe_monotony']}, rpe_strain={row['rpe_strain']}
                WHERE id={row['id']}
            '''
            conn.cursor().execute(sql_str)
            if print_progress:
                print(f'{t_count/t_total:.2%} {datetime.datetime.now() - st} {table_name}', '               ', end='\r')

    conn.commit()
    conn.close()
    print(f'100% {datetime.datetime.now() - st} {table_name}', '               ')


def save_workouts(conn, d_date, d_type, d_values, workouts):
    aggregation_keys = [[ACTIVITY, ACTIVITY_TYPE, EQUIPMENT],
                        [ACTIVITY_TYPE, EQUIPMENT],
                        [ACTIVITY, EQUIPMENT],
                        [ACTIVITY, ACTIVITY_TYPE],
                        [EQUIPMENT],
                        [ACTIVITY],
                        [ACTIVITY_TYPE],
                        []
                        ]
    for a in aggregation_keys:
        agg_workouts = aggregate_workouts(workouts, a)
        for w in agg_workouts:
            save_workout(conn, d_date, d_type, d_values, w, a)


def save_workout(conn, d_date, d_type, d_values, workout, keys):

    a = 'All'
    at = 'All'
    e_name = 'All'

    if ACTIVITY in keys:
        a = workout[ACTIVITY]
    if ACTIVITY_TYPE in keys:
        at = workout[ACTIVITY_TYPE]
    if EQUIPMENT in keys:
        e_name = workout[EQUIPMENT].replace(' ', '')

    _ = create_table(DAY, a, at, e_name, conn)

    w_values = value_string_for_sql(workout, workout_map)

    col_names = f'{day_col_names}, {workout_col_names}'
    d_values = f'{d_values}, {w_values}'

    execute_day_sql(conn, d_date, d_type, col_names, d_values, activity=a, activity_type=at, equipment_name=e_name)


# take workouts and combine those that have same Activity:Type:Equipment
def aggregate_workouts(workouts, keys):
    agg_w = dict()
    for w in workouts:
        key = 'key'
        if len(keys) > 0:
            key = ':'.join([w[k] for k in keys])
        if EQUIPMENT in keys and (w[EQUIPMENT] == NOT_SET or w[EQUIPMENT] == ''):
            continue
        if key in agg_w:
            agg_w[key].append(dict(w))
        else:
            agg_w[key] = [dict(w)]
    result = []
    for w_array in agg_w.values():
        if len(w_array) == 1:
            result.append(w_array[0])
        else:
            d = dict()
            d[ACTIVITY] = w_array[0][ACTIVITY]
            d[ACTIVITY_TYPE] = w_array[0][ACTIVITY_TYPE]
            d[EQUIPMENT] = w_array[0][EQUIPMENT]
            for map in workout_map:
                r = 0
                for w in w_array:
                    if MAPPER in map:
                        value = eval(f'{map[MAPPER]}({w})')
                    else:
                        value = w[map[JSON]]
                    if map[AGGREGATION_METHOD] == SUM:
                        r += value
                    else:
                        r += value * w['seconds']
                d[map[JSON]] = r
            for map in workout_map:
                if map[AGGREGATION_METHOD] == MEAN:
                    d[map[JSON]] = d[map[JSON]] / d['seconds']
                    if map[TYPE] == INTEGER:
                        d[map[JSON]] = int(d[map[JSON]])
            result.append(d)

    return result


def value_string_for_sql(dictionary, json_map):
    d_value_array = []
    for m in json_map:
        if MAPPER in m:
            value = eval(f'{m[MAPPER]}({dictionary})')
            d_value_array.append(str(value))
        elif m[TYPE] == INTEGER:
            d_value_array.append(str(int(round(float(dictionary[m[JSON]]) * m[FACTOR], 0))))
        elif m[TYPE] == REAL:
            d_value_array.append(str(round(float(dictionary[m[JSON]]) * m[FACTOR],2)))
        elif m[TYPE] == BOOLEAN:
            if dictionary[m[JSON]] == 0:
                d_value_array.append('0')
            else:
                d_value_array.append('1')
        else:
            d_value_array.append(f"'{dictionary[m[JSON]]}'")

    return ','.join([s for s in d_value_array])


def day_exists(d, table, conn):
    sql_str = f'''
            SELECT id FROM {table} WHERE date="{d}"
    '''
    result = conn.cursor().execute(sql_str)
    return len(result.fetchall()) > 0


def create_table(period, activity, activity_type, equipment_name, conn):

    table_name = f'{period}_{activity}_{activity_type}_{equipment_name}'

    sql_str = f'''
    
        CREATE TABLE {table_name}
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE UNIQUE,
        year_week VARCHAR(16),
        year_month VARCHAR(16),
        day_of_week VARCHAR(8),
        month VARCHAR(8),
        day_type VARCHAR(16),
        {day_col_creation},
        {workout_col_creation},
        {calculated_col_creation},
        {physiological_col_creation})
        '''

    try:
        conn.cursor().execute(sql_str)
        conn.commit()
        table_names.add(table_name)

        sql_str = f"""

            INSERT INTO Tables
            (period, activity, activity_type, equipment, table_name)
            VALUES
            ('{period}',
            '{activity}',
            '{activity_type}',
            '{equipment_name}',
            '{table_name}'
            )

        """
        conn.cursor().execute(sql_str)
        conn.commit()

    except Exception as e:
        pass

    return table_name


def execute_day_sql(conn, d_date, d_type, col_names, values, activity='All', activity_type='All', equipment_name='All', table_name=None):

    t_name = table_name
    if table_name is None:
        t_name = f'{DAY}_{activity}_{activity_type}_{equipment_name}'

    d_month = f'{d_date.year}-{d_date.strftime("%b")}'
    d_week = f'{d_date.year}-{d_date.isocalendar()[1]}'
    d_day = d_date.strftime('%a')
    month = d_date.strftime('%b')

    sql_str = f'''

        INSERT INTO {t_name}
        (date, year_week, year_month, day_of_week, month, day_type, {col_names})
        VALUES
        (
        '{d_date}',
        '{d_week}',
        '{d_month}',
        '{d_day}',
        '{month}',
        '{d_type}',
        {values}
        )
    '''

    try:
        conn.cursor().execute(sql_str)
        # conn.commit()
    except Exception as e:
        print(e)

def create_agg_and_insert_str_for_sql():
    aggregate_array = ['MAX(date)']
    insert_array = ['date']
    for m in (workout_map + day_map + calculated_map):
        if AGGREGATION_METHOD in m:
            if m[AGGREGATION_METHOD] == SUM:
                aggregate_array.append(f'SUM({m[DB_COL]})')
                insert_array.append(m[DB_COL])
            elif m[AGGREGATION_METHOD] == MEAN:
                aggregate_array.append(f'AVG({m[DB_COL]})')
                insert_array.append(m[DB_COL])

    return ','.join(aggregate_array), ','.join(insert_array)


def mph_mapper(workout_dict):
    result = 0.0
    if 'km' in workout_dict and 'seconds' in workout_dict:
        seconds = float(workout_dict['seconds'])
        if seconds > 0:
            result = round(float(workout_dict['km']) * MILES_PER_KM * 60 * 60 / float(workout_dict['seconds']), 1)

    return result


def kph_mapper(workout_dict):
    result = 0.0
    if 'km' in workout_dict and 'seconds' in workout_dict:
        seconds = float(workout_dict['seconds'])
        if seconds > 0:
            result = round(float(workout_dict['km']) * 60 * 60 / float(workout_dict['seconds']), 1)

    return result


def rpe_tss_mapper(workout_dict):
    result = 0.0
    if 'rpe' in workout_dict and 'seconds' in workout_dict:
        seconds = float(workout_dict['seconds'])
        rpe = float(workout_dict['rpe'])
        if seconds > 0:
            #  factor is (100/49)/3600 -  to make rep 7 for an hour 100 TSS.
            #  This is 1 / (49 * 36)
            result = round(rpe * rpe * seconds / (49 * 36), 1)

    return result

ALL = 'all'
DAY = 'day'
FAT = 'fat'
HRV = 'hrv'
TSB = 'tsb'
STRAIN = 'strain'
PRINT_PROGRESS = 'pp'

import sys
if __name__ == '__main__':

    all =day = fat = hrv = tsb = strain = False
    print_progress = False
    if PRINT_PROGRESS in sys.argv:
        print_progress = True

    if ALL in sys.argv or len(sys.argv) == 0:
        all = True
    if DAY in sys.argv:
        day = True
    if FAT in sys.argv:
        fat = True
    if HRV in sys.argv:
        hrv = True
    if TSB in sys.argv:
        tsb = True
    if STRAIN in sys.argv:
        strain = True

    if all or day:
        print('Basic day info...')
        populate(print_progress)

    if all or fat:
        print('KG / Fat%...')
        populate_kg_fat_percent(print_progress)

    if all or hrv:
        print('HRV...')
        populate_hr_sdnn_rmssd(print_progress)

    if all or tsb:
        print('Calculating TSB ...')
        calculate_all_tsb(print_progress)

    if all or strain:
        print('Calculating Strain ...')
        calculate_all_strain(print_progress)

