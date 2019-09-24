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

    def generate_from_date(self, date, print_progress=False):
        if date is None or date == '':
            from . import DataWarehouse
            last_date_str = DataWarehouse.instance().max_date()
            if last_date_str is None:
                from_date = None
            else:
                from_date = dateutil.parser.parse(last_date_str).date() + datetime.timedelta(days=1)
        else:
            from_date = date
            self.__delete_entries_from(date)
        self.generate(print_progress=print_progress, from_date=from_date)

    def generate(self, print_progress=False, from_date=None):
        start = datetime.datetime.now()
        if print_progress:
            print("getting all days...")
        if from_date is None:
            days = TrainingDataManager().days()
        else:
            days = TrainingDataManager().days_since(from_date)
        if print_progress:
            print(f"Done in {datetime.datetime.now()-start}")
            print(f"Populating for days")
        tables = self.__tables_dict()
        for d in days:
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
            if print_progress:
                print(f'{datetime.datetime.now() - start} {d.date}', end='\r')

        for t in tables:
            if print_progress:
                print(f'{t}: TSB, monotony, strain')
            self.__populate_tsb_monotony_strain(t, from_date=from_date)
            if print_progress:
                print(f'{t}: interpolating values')
            self.__interpolate_zeroes(t, from_date=from_date)

        #NB this must be after interpolation is done
        self.__calculate_hrv_limits(tables, from_date=from_date)

    def __delete_entries_from(self, date):
        for t in self.__tables():
            self.__conn.execute(f"DELETE FROM {t} WHERE date>='{date}'")
        self.__conn.commit()

    def __tables_dict(self):
        r_dict = dict()
        for t in self.__tables():
            r_dict[t] = WorkoutType.workout_type_for_col_name(t)
        return r_dict

    def __tables(self):
        return [i[0] for i in self.__conn.execute(f'SELECT table_name FROM Tables').fetchall()]

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

    def __populate_tsb_monotony_strain(self, table, from_date=None):
        c = self.__conn.cursor()
        ctl = rpe_ctl = atl = rpe_atl = 0.0
        if from_date is None:
            data = c.execute(f"SELECT date, tss, rpe_tss from {table} ORDER BY date ASC").fetchall()
        else:
            date = dateutil.parser.parse(str(from_date)).date() - datetime.timedelta(days=1)
            starting_values = c.execute(f'SELECT ctl, rpe_ctl, atl, rpe_atl FROM {table} where date="{str(date)}"').fetchall()[0]
            ctl = starting_values[0]
            rpe_ctl = starting_values[1]
            atl = starting_values[2]
            rpe_atl = starting_values[3]
            data = c.execute(f"SELECT date, tss, rpe_tss from {table} WHERE date>='{from_date}' ORDER BY date ASC").fetchall()

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
        if from_date is None:
            # get all the data
            df = pd.read_sql(f"SELECT date, tss, rpe_tss from {table} ORDER BY date ASC", self.__conn)
        else:
            date = dateutil.parser.parse(str(from_date)).date() - datetime.timedelta(days=self.STRAIN_DAYS)
            df = pd.read_sql(f"SELECT date, tss, rpe_tss from {table} WHERE date>='{str(date)}' ORDER BY date ASC", self.__conn)
        min_periods = 1
        df['tss_stdev'] = df['tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).std().clip(lower=0.01)
        df['rpe_tss_stdev'] = df['rpe_tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).std().clip(lower=0.01)
        df['monotony'] = df['tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).mean() / df['tss_stdev']
        df['strain'] = df['tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).sum() * df['monotony']
        df['rpe_monotony'] = df['rpe_tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).mean() / df['rpe_tss_stdev']
        df['rpe_strain'] = df['rpe_tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).sum() * df['rpe_monotony']
        df.fillna(0, inplace=True)

        if from_date is not None:
            # need to filter the df to the dates we want
            filtered_df = df.loc[df['date'] >= str(from_date)]
        else:
            filtered_df = df

        for index, row in filtered_df.iterrows():
            sql_str = f'''
                    UPDATE {table} SET
                    monotony={row['monotony']}, strain={row['strain']}, 
                    rpe_monotony={row['rpe_monotony']}, rpe_strain={row['rpe_strain']}
                    WHERE date='{row['date']}'
                '''
            c.execute(sql_str)
        self.__conn.commit()

    def __interpolate_zeroes(self, table, from_date=None):
        from . import WarehouseColumn
        for col in WarehouseColumn.interpolated_columns():
            if from_date is None:
                df = pd.read_sql_query(f'SELECT date, {col} FROM {table}', self.__conn)
            else:
                # need to find date of last recording per from_date and interpolae from there
                sql = f'SELECT max(date) FROM {table} WHERE date<"{from_date}" AND {WarehouseColumn(col).recorded_column_name()}=1'
                date = self.__conn.execute(sql).fetchall()[0][0]
                df = pd.read_sql_query(f'SELECT date, {col} FROM {table} WHERE date>="{date}"', self.__conn)

            df = df.replace(0, np.NaN)
            # 'both' means it interpolate initial zeroes as well as final ones
            df.interpolate(inplace=True, limit_direction='both')
            for index, row in df.iterrows():
                sql = f'''
                    UPDATE {table} SET
                    {col}={row[col]}
                    WHERE date='{row['date']}'
                '''
                self.__conn.cursor().execute(sql)
        self.__conn.commit()

    def __calculate_hrv_limits(self, tables, from_date=None):
        min_periods = 1
        if from_date is None:
            sql = f"SELECT date, sdnn, rmssd from day_All_All_All ORDER BY date ASC"
        else:
            date = dateutil.parser.parse(str(from_date)).date() - datetime.timedelta(days=self.HRV_DAYS)
            sql = f"SELECT date, sdnn, rmssd from day_All_All_All WHERE date>='{date}' ORDER BY date ASC"

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

        if from_date is not None:
            # need to filter the df to the dates we want
            filtered_df_all = df.loc[df['date'] >= str(from_date)]
        else:
            filtered_df_all = df


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
