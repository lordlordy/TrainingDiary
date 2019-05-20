import sqlite3
import pandas as pd
import numpy as np
import dateutil.parser


class DataWarehouse:

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
    aggregators = [SUM, MEAN, MAX, MEDIAN, MIN]

    @classmethod
    def instance(cls):
        return DataWarehouse()

    def __init__(self):
        self.__conn = sqlite3.connect('training_data_warehouse.sqlite3')

        sql_str = f'''
            SELECT * FROM DAY_All_All_All
            LIMIT 0,5
        '''

        df = pd.read_sql_query(sql_str, self.__conn)

        self.__float64_cols = []
        self.__int64_cols = []

        for key, value in df.dtypes.iteritems():
            if key == 'id': continue

            if value == np.float64:
                self.__float64_cols.append(key)
            elif value == np.int64:
                self.__int64_cols.append(key)

    def float_column_names(self):
        return self.__float64_cols

    def int_column_names(self):
        return self.__int64_cols

    def day_types(self):
        dt = self.__conn.execute(f'SELECT DISTINCT day_type FROM Day_All_All_All')
        return ['All'] + sorted([t[0] for t in dt])

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

        print(f'Period: {period}')
        print(f'aggregation: {aggregation}')
        print(f'activity {activity}')
        print(f'activity_type: {activity_type}')
        print(f'equipment: {equipment}')
        print(f'measure: {measure}')
        print(f'to_date: {to_date}')
        print(f'rolling: {rolling}')
        print(f'rolling_periods: {rolling_periods}')
        print(f'rolling_aggregation: {rolling_aggregation}')
        print(f'day_of_week: {day_of_week}')
        print(f'month: {month}')
        print(f'day_type: {day_type}')

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

            return s

        except Exception as e:
            print('Error in creating series')
            print('Series Index:')
            print(s.index)
            print(e)
            return None


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

                ltd_history.append((i, ed_num, plus_one, v))

            if v >= annual_ed_num + 1:
                # this contributes to annual
                this_years_annual_contributors_to_next = np.append(this_years_annual_contributors_to_next, v)
                annual_plus_one = (annual_ed_num + 1) - this_years_annual_contributors_to_next.size
                if annual_plus_one == 0:
                    annual_ed_num += 1
                    this_years_annual_contributors_to_next = this_years_annual_contributors_to_next[this_years_annual_contributors_to_next >= annual_ed_num+1]
                    # recalc +1
                    annual_plus_one = (annual_ed_num + 1) - this_years_annual_contributors_to_next.size
                annual_history.append((i, annual_ed_num, annual_plus_one, v))

        annual_summary.append((current_year, annual_ed_num, annual_plus_one))


        return (ed_num, ltd_history, annual_history, annual_summary)

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