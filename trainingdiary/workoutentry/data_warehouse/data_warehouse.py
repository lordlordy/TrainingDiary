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

    def time_series(self, activity, activity_type, equipment, measure):
