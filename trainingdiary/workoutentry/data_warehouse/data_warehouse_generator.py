import sqlite3
from workoutentry.training_data import TrainingDataManager
from workoutentry.models import WorkoutType
import datetime
import dateutil
import numpy as np
import pandas as pd


class DataWarehouseGenerator:

    def __init__(self, warehouse_name):
        self.__conn = sqlite3.connect(warehouse_name)
        try:
            c = self.__conn.cursor()
            c.execute('''
                        CREATE TABLE Tables(
                        period varchar(16) NOT NULL,
                        activity varchar(16) NOT NULL,
                        activity_type varchar(16) NOT NULL,
                        equipment varchar (16) NOT NULL,
                        table_name varchar(64) NOT NULL,
                        first_date DATE NOT NULL,
                        PRIMARY KEY (table_name));
            ''')
        except Exception as e:
            print(e)
            print("continuing")
            pass
        from . import WarehouseColumn

        self.__column_names = ','.join(WarehouseColumn.day_cols())
        self.CTL_DECAY_DAYS = 42
        self.CTL_IMPACT_DAYS = 42
        self.ATL_DECAY_DAYS = 7
        self.ATL_IMPACT_DAYS = 7
        self.CTL_DECAY = np.exp(-1 / self.CTL_DECAY_DAYS)
        self.CTL_IMPACT = 1 - np.exp(-1 / self.CTL_IMPACT_DAYS)
        self.ATL_DECAY = np.exp(-1 / self.ATL_DECAY_DAYS)
        self.ATL_IMPACT = 1 - np.exp(-1 / self.ATL_IMPACT_DAYS)
        self.STRAIN_DAYS = 91
        self.HRV_DAYS = 91
        self.HRV_OFF_PERCENTILE = 0.05
        self.HRV_EASY_PERCENTILE = 0.25
        self.HRV_HARD_PERCENTILE = 0.75
        self.HRV_OFF_SDs = DataWarehouseGenerator.normal_cdf_inverse(self.HRV_OFF_PERCENTILE)
        self.HRV_EASY_SDs = DataWarehouseGenerator.normal_cdf_inverse(self.HRV_EASY_PERCENTILE)
        self.HRV_HARD_SDs = DataWarehouseGenerator.normal_cdf_inverse(self.HRV_HARD_PERCENTILE)

    def generate_from_date(self, from_date, print_progress=False):
        start_date_str = from_date
        if from_date is None or from_date == '':
            from . import DataWarehouse
            start_date_str = DataWarehouse.instance().max_date()
            if start_date_str is None:
                # no data warehouse entries so start from first date we have in TrainingData
                start_date_str = TrainingDataManager().earliest_date()
            else:
                # start the day after the last date in the warehouse
                start_date_str = str(dateutil.parser.parse(start_date_str).date() + datetime.timedelta(days=1))

        self.generate(from_date=start_date_str, to_date=TrainingDataManager().latest_date(),
                      print_progress=print_progress)

    def generate(self, from_date, to_date, print_progress=False):

        self.update_days(from_date=from_date, to_date=to_date, print_progress=print_progress)

        self.generate_tsb_monotony_strain(from_date=from_date, to_date=to_date,
                                          print_progress=print_progress)
        from . import WarehouseColumn
        for col in WarehouseColumn.interpolated_columns():
            self.interpolate_zeroes(from_date=from_date, to_date=to_date, for_column=col, print_progress=print_progress)

        #NB this must be after interpolation is done
        self.generate_hrv_limits(from_date=from_date, to_date=to_date)
        print('ALL DONE')

    def update_days(self, from_date, to_date, print_progress=False):
        start = datetime.datetime.now()

        start_date, end_date = self.__correct_bounds(from_date=from_date, to_date=to_date)
        self.__delete_entries_in_range(start_date, end_date)

        current_date = dateutil.parser.parse(start_date).date()
        last_date = dateutil.parser.parse(end_date).date()

        print(f"Populating for days")
        tables = self.__tables_dict()
        count = 0
        while current_date <= last_date:
            count += 1
            d = TrainingDataManager().day_for_date(current_date)
            # create new tables as required
            for t in d.workout_types():
                table_name = f"day_{str(t)}"
                if table_name not in tables:
                    try:
                        self.__create_table(table_name, t, d.date)
                        tables[table_name] = t
                    except Exception as e:
                        if print_progress:
                            print(f'Table probably exists so continuing. {e}')
                        pass
            # add row for this day to all existing tables
            for key, value in tables.items():
                self.__insert_row(key, value, d)
            if print_progress or count % 100 == 0:
                print(f'{count} - {datetime.datetime.now() - start} {d.date}', end='\r')
            current_date = current_date + datetime.timedelta(days=1)

    def generate_hrv_limits(self, from_date, to_date, print_progress=None):
        start_date, end_date = self.__correct_bounds(from_date=from_date, to_date=to_date)
        self.__calculate_hrv_limits(self.__tables_dict(), from_date=start_date, to_date=end_date,
                                    print_progress=print_progress)

    def generate_tsb_monotony_strain(self, from_date, to_date, print_progress=False):
        print("TSB, Monotony, Strain")
        start_date, end_date = self.__correct_bounds(from_date=from_date, to_date=to_date)
        for t in self.__tables_dict():
            if print_progress:
                print(f'{t}: TSB, monotony, strain')
            self.populate_tsb_monotony_strain_for_table(t, from_date=start_date, to_date=end_date)

    def interpolate_zeroes(self, from_date, to_date, for_column, print_progress=False):
        start_date, end_date = self.__correct_bounds(from_date=from_date, to_date=to_date)
        self.__interpolate_zeroes(from_date=start_date, to_date=end_date, for_column=for_column,
                                  print_progress=print_progress)

    def __correct_bounds(self, from_date, to_date):
        earliest_date = TrainingDataManager().earliest_date()
        latest_date = TrainingDataManager().latest_date()
        start_date = from_date if from_date >= earliest_date else earliest_date
        end_date = to_date if to_date <= latest_date else latest_date
        return (start_date, end_date)

    def __delete_entries_from(self, date):
        for t in self.__tables():
            self.__conn.execute(f"DELETE FROM {t} WHERE date>='{date}'")
        self.__conn.commit()

    def __delete_entries_in_range(self, from_date, to_date):
        for t in self.__tables():
            self.__conn.execute(f"DELETE FROM {t} WHERE date>='{from_date}' AND date<='{to_date}'")
        self.__conn.commit()

    def __tables_dict(self):
        r_dict = dict()
        for t in self.__tables():
            r_dict[t] = WorkoutType.workout_type_for_col_name(t)
        return r_dict

    def __tables(self):
        return [i[0] for i in self.__conn.execute(f'SELECT table_name FROM Tables').fetchall()]

    def __tables_first_date_dictionary(self):
        tables = self.__conn.execute('SELECT table_name, first_date FROM Tables').fetchall()
        d = dict()
        for t in tables:
            d[t[0]] = t[1]
        return d

    def __create_table(self, table_name, workout_type, first_date):
        c = self.__conn.cursor()
        from . import WarehouseColumn
        column_defs = [WarehouseColumn(c).sql_str() for c in WarehouseColumn.day_cols()]
        sql = f'CREATE TABLE {table_name} ({",".join(column_defs)});'
        c.execute(sql)
        c.execute(f'''
            INSERT INTO Tables
            (period, activity, activity_type, equipment, table_name, first_date)
            VALUES
            ("day", "{'All' if workout_type.activity is None else workout_type.activity}",
            "{'All' if workout_type.activity_type is None else workout_type.activity_type}",
            "{'All' if workout_type.equipment is None else workout_type.equipment}",
            "{table_name}", "{first_date}")
            ''')
        self.__conn.commit()

    def __insert_row(self, table, workout_type, day):
        cols = []
        values = []
        for key, value in day.warehouse_dictionary(workout_type).items():
            cols.append(key.name)
            values.append(str(value))

        sql = f'''
            INSERT INTO {table}
            ({','.join(cols)})
            VALUES
            ({','.join(values)})
        '''

        self.__conn.cursor().execute(sql)
        self.__conn.commit()

    def populate_tsb_monotony_strain_for_table(self, table, from_date, to_date):
        c = self.__conn.cursor()
        ctl = rpe_ctl = atl = rpe_atl = 0.0
        date = dateutil.parser.parse(str(from_date)).date() - datetime.timedelta(days=1)
        starting_values = c.execute(f'SELECT ctl, rpe_ctl, atl, rpe_atl FROM {table} where date="{str(date)}"').fetchall()
        if len(starting_values) > 0:
            ctl = starting_values[0][0]
            rpe_ctl = starting_values[0][1]
            atl = starting_values[0][2]
            rpe_atl = starting_values[0][3]
        data = c.execute(f'''
            SELECT date, tss, rpe_tss from {table} 
            WHERE date>='{from_date}' AND date<='{to_date}' ORDER BY date ASC
            ''').fetchall()

        # Training Stress Balance
        for d in data:
            ctl = d[1] * self.CTL_IMPACT + ctl * self.CTL_DECAY
            rpe_ctl = d[2] * self.CTL_IMPACT + rpe_ctl * self.CTL_DECAY
            atl = d[1] * self.ATL_IMPACT + atl * self.ATL_DECAY
            rpe_atl = d[2] * self.ATL_IMPACT + rpe_atl * self.ATL_DECAY

            c.execute(f'''
                UPDATE {table}
                SET ctl={ctl}, atl={atl}, tsb={ctl-atl}, rpe_ctl={rpe_ctl}, rpe_atl={rpe_atl}, rpe_tsb={rpe_ctl-rpe_atl}
                WHERE date='{d[0]}'
            ''')

        self.__conn.commit()

        # Monotony and Strain - if from_date set we need to go STRAIN_DAYS prior to calculate
        date = dateutil.parser.parse(str(from_date)).date() - datetime.timedelta(days=self.STRAIN_DAYS)
        df = pd.read_sql(f"""
            SELECT date, tss, rpe_tss from {table} 
            WHERE date>='{str(date)}' AND date<='{to_date}' ORDER BY date ASC
            """, self.__conn)
        min_periods = 1
        df['tss_stdev'] = df['tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).std().clip(lower=0.01)
        df['rpe_tss_stdev'] = df['rpe_tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).std().clip(lower=0.01)
        df['monotony'] = df['tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).mean() / df['tss_stdev']
        df['strain'] = df['tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).sum() * df['monotony']
        df['rpe_monotony'] = df['rpe_tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).mean() / df['rpe_tss_stdev']
        df['rpe_strain'] = df['rpe_tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).sum() * df['rpe_monotony']
        df.fillna(0, inplace=True)

        # need to filter the df to the dates we want
        filtered_df = df.loc[df['date'] >= str(from_date)]

        for index, row in filtered_df.iterrows():
            sql_str = f'''
                    UPDATE {table} SET
                    monotony={row['monotony']}, strain={row['strain']}, 
                    rpe_monotony={row['rpe_monotony']}, rpe_strain={row['rpe_strain']}
                    WHERE date='{row['date']}'
                '''
            c.execute(sql_str)
        self.__conn.commit()

    def __interpolate_zeroes(self, from_date, to_date, for_column, print_progress):
        from . import WarehouseColumn
        # for col in WarehouseColumn.interpolated_columns():
        if print_progress:
            print(f'Interpolating {for_column}')
        # need to find date of last recording pre from_date and interpolate from there
        sql = f"""
            SELECT max(date) FROM day_All_All_All 
            WHERE date<"{from_date}" AND {WarehouseColumn(for_column).recorded_column_name()}=1
            """
        date = self.__conn.execute(sql).fetchall()[0][0]
        if date is None:
            # no recording prior to the from_date. Lets find first recording post and start from there
            sql = f"""
                SELECT min(date) FROM day_All_All_All
                WHERE date>='{from_date}' AND {WarehouseColumn(for_column).recorded_column_name()}=1
                """
            date = self.__conn.execute(sql).fetchall()[0][0]
            if date is None:
                # no recordings so nothing to interpolate
                return

        recorded = WarehouseColumn(for_column).recorded_column_name()
        df = pd.read_sql_query(f'SELECT date, {for_column}, {recorded} FROM day_All_All_All WHERE date>="{date}" AND date<="{to_date}"',
                               self.__conn)

        recorded_values = df[recorded]
        df = df.replace(0, np.NaN)
        df[recorded] = recorded_values
        # 'both' means it interpolate initial zeroes as well as final ones
        try:
            df.interpolate(inplace=True, limit_direction='both')
            # have interpolated values. Lets stick them in each table
            for table_name, first_date in self.__tables_first_date_dictionary().items():
                if print_progress:
                    print(f'\t {table_name} - {first_date}')
                filtered_df = df.loc[df['date'] >= first_date]
                for index, row in filtered_df.iterrows():
                    if row[recorded] == 0:
                        sql = f'''
                            UPDATE {table_name} SET
                            {for_column}={row[for_column]}
                            WHERE date='{row['date']}'
                        '''
                        self.__conn.cursor().execute(sql)

            self.__conn.commit()

        except TypeError as e:
            print(for_column)
            print(df)
            print(e)


    def __calculate_hrv_limits(self, tables, from_date, to_date, print_progress):
        if print_progress:
            print("HRV Thresholds")
            print(f"\tday_All_All_All")
        min_periods = 1
        date = dateutil.parser.parse(str(from_date)).date() - datetime.timedelta(days=self.HRV_DAYS)
        sql = f"""
            SELECT date, sdnn, rmssd from day_All_All_All 
            WHERE date>='{date}' AND date<='{to_date}' ORDER BY date ASC
            """

        df = pd.read_sql(sql, self.__conn)
        df['sdnn_stdev'] = df['sdnn'].rolling(self.HRV_DAYS, min_periods=min_periods).std().clip(lower=0.01)
        df['sdnn_mean'] = df['sdnn'].rolling(self.HRV_DAYS, min_periods=min_periods).mean().clip(lower=0.01)
        df['rmssd_stdev'] = df['rmssd'].rolling(self.HRV_DAYS, min_periods=min_periods).std().clip(lower=0.01)
        df['rmssd_mean'] = df['rmssd'].rolling(self.HRV_DAYS, min_periods=min_periods).mean().clip(lower=0.01)
        df.fillna(0, inplace=True)
        df['sdnn_off'] = df['sdnn_mean'] + df['sdnn_stdev'] * self.HRV_OFF_SDs
        df['sdnn_easy'] = df['sdnn_mean'] + df['sdnn_stdev'] * self.HRV_EASY_SDs
        df['sdnn_hard'] = df['sdnn_mean'] + df['sdnn_stdev'] * self.HRV_HARD_SDs
        df['rmssd_off'] = df['rmssd_mean'] + df['rmssd_stdev'] * self.HRV_OFF_SDs
        df['rmssd_easy'] = df['rmssd_mean'] + df['rmssd_stdev'] * self.HRV_EASY_SDs
        df['rmssd_hard'] = df['rmssd_mean'] + df['rmssd_stdev'] * self.HRV_HARD_SDs

        # need to filter the df to the dates we want
        filtered_df_all = df.loc[df['date'] >= str(from_date)]

        for index, row in filtered_df_all.iterrows():
            sql = f'''
                UPDATE day_All_All_All SET
                sdnn_off={row['sdnn_off']}, sdnn_easy={row['sdnn_easy']}, sdnn_hard={row['sdnn_hard']},
                sdnn_mean={row['sdnn_mean']}, sdnn_std_dev={row['sdnn_stdev']}, rmssd_off={row['rmssd_off']}, 
                rmssd_easy={row['rmssd_easy']}, rmssd_hard={row['rmssd_hard']}, rmssd_mean={row['rmssd_mean']}, 
                rmssd_std_dev={row['rmssd_stdev']}
                WHERE date='{row['date']}'
            '''
            self.__conn.cursor().execute(sql)
        self.__conn.commit()

        # do all other tables
        for key, value in tables.items():
            if key == "day_All_All_All":
                continue
            if print_progress:
                print(f"\t{key}")
            min_max = self.__conn.cursor().execute(f'SELECT min(date), max(date) FROM {key}').fetchall()
            filtered_df = filtered_df_all.loc[(df['date'] >= min_max[0][0]) & (df['date'] <= min_max[0][1])]
            for index, row in filtered_df.iterrows():
                sql = f'''
                    UPDATE {key} SET
                    sdnn_off={row['sdnn_off']}, sdnn_easy={row['sdnn_easy']}, sdnn_hard={row['sdnn_hard']},
                    sdnn_mean={row['sdnn_mean']}, sdnn_std_dev={row['sdnn_stdev']}, rmssd_off={row['rmssd_off']}, 
                    rmssd_easy={row['rmssd_easy']}, rmssd_hard={row['rmssd_hard']}, rmssd_mean={row['rmssd_mean']}, 
                    rmssd_std_dev={row['rmssd_stdev']}
                    WHERE date='{row['date']}'
                '''
                self.__conn.cursor().execute(sql)
            self.__conn.commit()


    # Implementation from https://www.johndcook.com/blog/csharp_phi_inverse/
    @classmethod
    def rational_approximation(cls, t):
        # Abramowitz and Stegun formula 26.2.23.
        # The absolute value of the error should be less than 4.5 e-4.
        c = [2.515517, 0.802853, 0.010328]
        d = [1.432788, 0.189269, 0.001308]
        return t - ((c[2]*t + c[1])*t + c[0]) / (((d[2]*t + d[1])*t + d[0])*t + 1.0)

    # Implementation from https://www.johndcook.com/blog/csharp_phi_inverse/
    # this takes a percentile (probability) and returns number of SD from mean
    @classmethod
    def normal_cdf_inverse(cls, p):
        if p <= 0.0 or p >= 1.0:
            print("Invalid input argument: \(p) in normal_cdf_inverse")

        # See article above for explanation of this section.
        if p < 0.5:
            # F^-1(p) = - G^-1(p)
            return -cls.rational_approximation(np.sqrt(-2.0 * np.log(p)))
        else:
            # F^-1(p) = G^-1(1-p)
            return cls.rational_approximation(np.sqrt(-2.0 * np.log(1.0 - p)))
