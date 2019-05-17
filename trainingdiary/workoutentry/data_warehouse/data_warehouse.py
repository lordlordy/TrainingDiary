import sqlite3
import pandas as pd
import numpy as np


class DataWarehouse:

    @classmethod
    def instance(cls):
        return DataWarehouse()

    def __init__(self):
        self.__conn = sqlite3.connect('training_data_warehouse.db')

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

    def time_series(self, period, activity, activity_type, equipment, measure):
        e = equipment.replace(" ",'')
        table_name = f'{period}_{activity}_{activity_type}_{e}'
        sql_str = f'''
        
            SELECT date, {measure}
            FROM {table_name}
            ORDER BY date
        
        '''
        try:
            df = pd.read_sql_query(sql_str,self.__conn)
            df['date'] = pd.to_datetime(df['date'])
            df['date'] = df['date'].dt.date
            df.set_index(['date'], inplace=True)
            return pd.Series(df[measure], name=measure)
        except Exception as e:
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