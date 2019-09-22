import sqlite3
import pandas as pd
from pandas.io.sql import DatabaseError
import numpy as np
import dateutil.parser
import datetime
import os
import trainingdiary
from .popular_graphs import create_popular_graphs

class DataWarehouse:

    PERIOD = 'period'
    AGGREGATION = 'aggregation'
    ACTIVITY = 'activity'
    ACTIVITY_TYPE = 'activity_type'
    EQUIPMENT = 'equipment'
    MEASURE = 'measure'
    TO_DATE = 'to_date'
    ROLLING = 'rolling'
    ROLLING_PERIODS = 'rolling_periods'
    ROLLING_AGGREGATION = 'rolling_aggregation'
    DAY_OF_WEEK = 'day_of_week'
    MONTH = 'month'
    DAY_TYPE = 'day_type'

    TIME_SERIES_VARIABLES = [PERIOD, AGGREGATION, ACTIVITY, ACTIVITY_TYPE, EQUIPMENT, MEASURE, TO_DATE, ROLLING,
                             ROLLING_PERIODS, ROLLING_AGGREGATION, DAY_OF_WEEK, MONTH, DAY_TYPE]

    popular_numbers = {
        'Daily Swim KM': {ACTIVITY: 'Swim', MEASURE: 'km'},
        'Daily Bike Miles': {ACTIVITY: 'Bike', MEASURE: 'miles'},
        'Daily Run Miles': {ACTIVITY: 'Run', MEASURE: 'miles'},
        'Weekly Swim KM': {ACTIVITY: 'Swim', MEASURE: 'km', PERIOD: 'W-Mon'},
        'Weekly Bike Miles': {ACTIVITY: 'Bike', MEASURE: 'miles', PERIOD: 'W-Mon'},
        'Weekly Run Miles': {ACTIVITY: 'Run', MEASURE: 'miles', PERIOD: 'W-Mon'},
        'Monthly Swim KM': {ACTIVITY: 'Swim', MEASURE: 'km', PERIOD: 'Month'},
        'Monthly Bike Miles': {ACTIVITY: 'Bike', MEASURE: 'miles', PERIOD: 'Month'},
        'Monthly Run Miles': {ACTIVITY: 'Run', MEASURE: 'miles', PERIOD: 'Month'},
        'Rolling Week Swim KM': {ACTIVITY: 'Swim', MEASURE: 'km', PERIOD: 'Day', ROLLING: 'Yes', ROLLING_PERIODS: '7'},
        'Rolling Week Bike Miles': {ACTIVITY: 'Bike', MEASURE: 'miles', PERIOD: 'Day', ROLLING: 'Yes', ROLLING_PERIODS: '7'},
        'Rolling Week Run Miles': {ACTIVITY: 'Run', MEASURE: 'miles', PERIOD: 'Day', ROLLING: 'Yes', ROLLING_PERIODS: '7'},
        'Rolling Month Swim KM': {ACTIVITY: 'Swim', MEASURE: 'km', PERIOD: 'Day', ROLLING: 'Yes', ROLLING_PERIODS: '30'},
        'Rolling Month Bike Miles': {ACTIVITY: 'Bike', MEASURE: 'miles', PERIOD: 'Day', ROLLING: 'Yes', ROLLING_PERIODS: '30'},
        'Rolling Month Run Miles': {ACTIVITY: 'Run', MEASURE: 'miles', PERIOD: 'Day', ROLLING: 'Yes', ROLLING_PERIODS: '30'},
        'Rolling Year Swim KM': {ACTIVITY: 'Swim', MEASURE: 'km', PERIOD: 'Day', ROLLING: 'Yes', ROLLING_PERIODS: '365'},
        'Rolling Year Bike Miles': {ACTIVITY: 'Bike', MEASURE: 'miles', PERIOD: 'Day', ROLLING: 'Yes', ROLLING_PERIODS: '365'},
        'Rolling Year Run Miles': {ACTIVITY: 'Run', MEASURE: 'miles', PERIOD: 'Day', ROLLING: 'Yes', ROLLING_PERIODS: '365'},
    }

    periods = ['Day', 'W-Mon', 'W-Tue', 'W-Wed', 'W-Thu', 'W-Fri', 'W-Sat', 'W-Sun', 'Month', 'Y-Jan',
               'Y-Feb', 'Y-Mar', 'Y-Apr', 'Y-May', 'Y-Jun', 'Y-Jul', 'Y-Aug', 'Y-Sep', 'Y-Oct', 'Y-Nov', 'Y-Dec',
               'Q-Jan', 'Q-Feb', 'Q-Mar']

    days_of_week = ['All', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    months = ['All', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    SUM = 'Sum'
    MEAN = 'Mean'
    MAX = 'Max'
    MEDIAN = 'Median'
    MIN = 'Min'
    STD_DEV = 'Std_Dev'
    aggregators = [SUM, MEAN, MAX, MEDIAN, MIN, STD_DEV]

    @classmethod
    def instance(cls):
        dw = DataWarehouse()
        if dw.base_table_built:
            dw.popular_graphs = create_popular_graphs(dw)
        return dw

    def __init__(self):
        db_path = os.path.join(trainingdiary.BASE_DIR, 'training_data_warehouse.sqlite3')
        self.__conn = sqlite3.connect(db_path)
        self.__float64_cols = []
        self.__int64_cols = []
        self.popular_graphs = []
        self.base_table_built = True

        sql_str = f'''
            SELECT * FROM Day_All_All_All
            LIMIT 0,5
        '''

        try:
            df = pd.read_sql_query(sql_str, self.__conn)

            for key, value in df.dtypes.iteritems():
                if key == 'id': continue

                if value == np.float64:
                    self.__float64_cols.append(key)
                elif value == np.int64:
                    self.__int64_cols.append(key)
        except DatabaseError as e:
            print('DataWarehouse instance not instantiated')
            print(e)
            self.base_table_built = False


    def float_column_names(self):
        return self.__float64_cols

    def int_column_names(self):
        return self.__int64_cols

    def day_types(self):
        dt = self.__conn.execute(f'SELECT DISTINCT day_type FROM Day_All_All_All')
        return ['All'] + sorted([t[0] for t in dt])

    def max_date(self):
        if self.base_table_built:
            date = self.__conn.execute('SELECT MAX(date) FROM Day_All_All_All')
            return [d[0] for d in date][0]
        else:
            return datetime.datetime.now().date()

    def min_date(self):
        if self.base_table_built:
            date = self.__conn.execute('SELECT MIN(date) FROM Day_All_All_All')
            return [d[0] for d in date][0]
        else:
            return datetime.datetime.now().date()

    def activities(self):
        activities = self.__conn.execute(f'SELECT DISTINCT activity FROM Tables')
        return sorted([a[0] for a in activities])

    def activity_types(self):
        activity_types = self.__conn.execute(f'SELECT DISTINCT activity_type FROM Tables')
        return sorted([a[0] for a in activity_types])

    def types_for_activity(self, activity):
        activity_types = self.__conn.execute(f'SELECT DISTINCT activity_type FROM Tables WHERE activity="{activity}"')
        return sorted([a[0] for a in activity_types])

    def equipment(self):
        equipment = self.__conn.execute(f'SELECT DISTINCT equipment FROM Tables')
        return sorted([a[0] for a in equipment])

    def equipment_for_activity_and_type(self, activity, activity_type):
        equipment = self.__conn.execute(f'SELECT DISTINCT equipment FROM Tables WHERE activity="{activity}" AND activity_type="{activity_type}"')
        return sorted([a[0] for a in equipment])

    def time_series(self, period='Day', aggregation='Sum', activity='All', activity_type='All', equipment='All',
                    measure='km', to_date=False, rolling=False, rolling_periods=0, rolling_aggregation='Sum',
                    day_of_week='All', month='All', day_type='All'):

        name = self._name(period=period, aggregation=aggregation, activity=activity, activity_type=activity_type,
                          equipment=equipment, measure=measure, to_date=to_date, rolling=rolling,
                          rolling_periods=rolling_periods, rolling_aggregation=rolling_aggregation, day_of_week=day_of_week,
                          month=month, day_type=day_type)

        e = equipment.replace(" ",'')
        if period != 'Day':
            if period == 'Month':
                period = 'M'
            else:
                period = period.replace('Y', 'A')

        where_clauses = []
        if day_of_week != 'All':
            where_clauses.append(f' day_of_week="{day_of_week}"')
        if month != 'All':
            where_clauses.append(f' month="{month}"')
        if day_type != 'All':
            where_clauses.append(f' day_type="{day_type}"')

        table_name = f'Day_{activity}_{activity_type}_{e}'
        if len(where_clauses) > 0:
            w_clause = ' AND '.join(where_clauses)
            sql_str = f'''
                SELECT date, {measure}
                FROM {table_name}
                WHERE {w_clause}
                ORDER BY date
            '''
        else:
            sql_str = f'''
                SELECT date, {measure}
                FROM {table_name}
                ORDER BY date
            '''
        try:
            df = pd.read_sql_query(sql_str,self.__conn)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index(['date'], inplace=True)
            s = pd.Series(df[measure], name=measure)
            if len(where_clauses) > 0:
                # re-index
                min_max = self.__conn.cursor().execute('SELECT MIN(date), MAX(date) FROM Day_All_All_All').fetchall()
                d_min = dateutil.parser.parse(min_max[0][0]).date()
                d_max = dateutil.parser.parse(min_max[0][1]).date()
                s = s.reindex(pd.date_range(d_min, d_max), fill_value=0)
            if period != 'Day':
                if aggregation == DataWarehouse.SUM:
                    if to_date:
                        s = s.groupby(pd.Grouper(freq=period)).expanding(0).sum()
                    else:
                        s = s.groupby(pd.Grouper(freq=period)).sum()
                elif aggregation == DataWarehouse.MEAN:
                    if to_date:
                        s = s.groupby(pd.Grouper(freq=period)).expanding().mean()
                    else:
                        s = s.groupby(pd.Grouper(freq=period)).mean()
                elif aggregation == DataWarehouse.MAX:
                    if to_date:
                        s = s.groupby(pd.Grouper(freq=period)).expanding().max()
                    else:
                        s = s.groupby(pd.Grouper(freq=period)).max()
                elif aggregation == DataWarehouse.MEDIAN:
                    if to_date:
                        s = s.groupby(pd.Grouper(freq=period)).expanding().median()
                    else:
                        s = s.groupby(pd.Grouper(freq=period)).median()
                elif aggregation == DataWarehouse.MIN:
                    if to_date:
                        s = s.groupby(pd.Grouper(freq=period)).expanding().min()
                    else:
                        s = s.groupby(pd.Grouper(freq=period)).min()
                elif aggregation == DataWarehouse.STD_DEV:
                    if to_date:
                        s = s.groupby(pd.Grouper(freq=period)).expanding().std()
                    else:
                        s = s.groupby(pd.Grouper(freq=period)).std()
                if to_date:
                    s = s.reset_index(level=0, drop=True)

            if rolling:
                if rolling_aggregation == DataWarehouse.SUM:
                    s = s.rolling(rolling_periods, min_periods=1).sum()
                elif rolling_aggregation == DataWarehouse.MEAN:
                    s = s.rolling(rolling_periods, min_periods=1).mean()
                elif rolling_aggregation == DataWarehouse.MAX:
                    s = s.rolling(rolling_periods, min_periods=1).max()
                elif rolling_aggregation == DataWarehouse.MEDIAN:
                    s = s.rolling(rolling_periods, min_periods=1).median()
                elif rolling_aggregation == DataWarehouse.MIN:
                    s = s.rolling(rolling_periods, min_periods=1).min()
                elif rolling_aggregation == DataWarehouse.STD_DEV:
                    s = s.rolling(rolling_periods, min_periods=1).std()
            return s, name

        except Exception as e:
            print('Error in creating series')
            print('Series Index:')
            print(e)
            return None, name


    def eddington_history(self, time_series):
        ltd_history = []
        annual_history = []
        annual_summary = []
        ltd_contributors_to_next = np.array([])
        this_years_annual_contributors_to_next = np.array([])
        ed_num = 0
        annual_ed_num = 0
        annual_plus_one = 0
        current_year = time_series.index[0].year

        time_series.sort_index(inplace=True)
        print(time_series)
        print(type(time_series))
        print(time_series.index)

        for i, v in time_series.iteritems():
            if i.year != current_year:
                annual_summary.append((current_year, annual_ed_num, annual_plus_one))
                # reset all the annual stuff
                current_year = i.year
                annual_ed_num = 0
                this_years_annual_contributors_to_next = np.array([])

            if v >= ed_num + 1:
                # this contributes to LTD
                ltd_contributors_to_next = np.append(ltd_contributors_to_next, v)
                plus_one = (ed_num + 1) - ltd_contributors_to_next.size
                if plus_one == 0:
                    ed_num += 1
                    # remove non contributoes as edd num increased
                    ltd_contributors_to_next = ltd_contributors_to_next[ltd_contributors_to_next >= ed_num+1]
                    # recalc +1
                    plus_one = (ed_num + 1) - ltd_contributors_to_next.size

                ltd_history.append((i.date(), ed_num, plus_one, round(v, 1)))

            if v >= annual_ed_num + 1:
                # this contributes to annual
                this_years_annual_contributors_to_next = np.append(this_years_annual_contributors_to_next, v)
                annual_plus_one = (annual_ed_num + 1) - this_years_annual_contributors_to_next.size
                if annual_plus_one == 0:
                    annual_ed_num += 1
                    this_years_annual_contributors_to_next = this_years_annual_contributors_to_next[this_years_annual_contributors_to_next >= annual_ed_num+1]
                    # recalc +1
                    annual_plus_one = (annual_ed_num + 1) - this_years_annual_contributors_to_next.size
                annual_history.append((i.date(), annual_ed_num, annual_plus_one, round(v, 1)))

        annual_summary.append((current_year, annual_ed_num, annual_plus_one))

        return ed_num, ltd_history, annual_history, annual_summary

    def _name(self, period='Day', aggregation='Sum', activity='All', activity_type='All', equipment='All',
                    measure='km', to_date=False, rolling=False, rolling_periods=0, rolling_aggregation='Sum',
                    day_of_week='All', month='All', day_type='All'):

        name_components = list()
        period_parts = list()
        period_parts.append(period)
        if to_date:
            period_parts.append(f'ToDate-{aggregation}')
        elif aggregation != 'Sum':
            period_parts.append(aggregation)
        name_components.append('-'.join(period_parts))
        if rolling:
            name_components.append(f'Rolling-{rolling_periods}-period-{rolling_aggregation}')
        name_components.append(activity)
        if activity_type != 'All':
            name_components.append(activity_type)
        if equipment != "All":
            name_components.append(equipment)
        name_components.append(measure)

        name = ':'.join(name_components)

        day_only = list()
        if day_of_week != 'All':
            day_only.append(day_of_week)
        if month != 'All':
            day_only.append(month)
        if day_type != 'All':
            day_only.append(day_type)

        if len(day_only) > 0:
            day_str = ' and '.join(day_only)
            name = f'{name} ({day_str})'

        return name

    def most_recent_recorded(self, item_name, before_date=None):
        if before_date is None:
            sql_str = f'SELECT date, {item_name} from day_All_All_All WHERE {item_name}_recorded=1 ORDER BY date DESC LIMIT 1'
        else:
            sql_str = f'SELECT date, {item_name} from day_All_All_All WHERE {item_name}_recorded=1 AND date<"{before_date}" ORDER BY date DESC LIMIT 1'
        data = self.__conn.cursor().execute(sql_str).fetchall()
        if len(data) > 0:
            return dateutil.parser.parse(data[0][0]).date(), data[0][1]
        else:
            return None, None


if __name__ == '__main__':
    s = DataWarehouse.instance().activities()
    print(s)
    for a in s:
        types = DataWarehouse.instance().types_for_activity(a)
        print(f'{a}: {types}')
        for t in types:
            equipment = DataWarehouse.instance().equipment_for_activity_and_type(a, t)
            print(f'{a}:{t}: {equipment}')

    print(DataWarehouse.instance().day_types())