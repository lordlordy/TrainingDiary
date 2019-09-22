import sqlite3
from workoutentry.training_data import TrainingDataManager
from datetime import datetime
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
        self.HRV_OFF_SDs = DataWarehouseGenerator.normalCDFInverse(self.HRV_OFF_PERCENTILE)
        self.HRV_EASY_SDs = DataWarehouseGenerator.normalCDFInverse(self.HRV_EASY_PERCENTILE)
        self.HRV_HARD_SDs = DataWarehouseGenerator.normalCDFInverse(self.HRV_HARD_PERCENTILE)

    def generate(self, print_progress=False):
        start = datetime.now()
        if print_progress:
            print("getting all days...")
        days = TrainingDataManager().days()
        if print_progress:
            print(f"Done in {datetime.now()-start}")
            print(f"Populating for days")
        tables = dict()
        for d in days:
            # create new tables as required
            for t in d.workout_types():
                table_name = f"day_{str(t)}"
                if table_name not in tables:
                    try:
                        self.create_table(table_name, t, d.date)
                        tables[table_name] = t
                    except Exception as e:
                        print(f'Table probably exists so continuing. {e}')
                        pass
            # add row for this day to all existing tables
            for key, value in tables.items():
                self.insert_row(key, value, d)
            if print_progress:
                print(f'{datetime.now() - start} {d.date}', end='\r')

        for t in tables:
            print(f'{t}: TSB, monotony, strain')
            self.populate_tsb_monotony_strain(t)
            print(f'{t}: interpolating values')
            self.interpolate_zeroes(t)

        #NB this must be after interpolation is done
        self.calculate_hrv_limits(tables)

    def create_table(self, table_name, workout_type, first_date):
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

    def insert_row(self, table, workout_type, day):
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

    def populate_tsb_monotony_strain(self, table):
        c = self.__conn.cursor()
        ctl = rpe_ctl = atl = rpe_atl = 0.0
        sql = f"SELECT date, tss, rpe_tss from {table} ORDER BY date ASC"
        data = c.execute(sql).fetchall()

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

        # Monotony and Strain
        min_periods = 1
        df = pd.read_sql(sql, self.__conn)
        df['tss_stdev'] = df['tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).std().clip(lower=0.01)
        df['rpe_tss_stdev'] = df['rpe_tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).std().clip(lower=0.01)
        df['monotony'] = df['tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).mean() / df['tss_stdev']
        df['strain'] = df['tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).sum() * df['monotony']
        df['rpe_monotony'] = df['rpe_tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).mean() / df['rpe_tss_stdev']
        df['rpe_strain'] = df['rpe_tss'].rolling(self.STRAIN_DAYS, min_periods=min_periods).sum() * df['rpe_monotony']
        df.fillna(0, inplace=True)

        for index, row in df.iterrows():
            sql_str = f'''
                    UPDATE {table} SET
                    monotony={row['monotony']}, strain={row['strain']}, 
                    rpe_monotony={row['rpe_monotony']}, rpe_strain={row['rpe_strain']}
                    WHERE date='{row['date']}'
                '''
            c.execute(sql_str)
        self.__conn.commit()

    def interpolate_zeroes(self, table):
        from . import WarehouseColumn
        for col in WarehouseColumn.interpolated_columns():
            df = pd.read_sql_query(f'SELECT date, {col} FROM {table}', self.__conn)
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

    def calculate_hrv_limits(self, tables):
        min_periods = 1
        sql = f"SELECT date, sdnn, rmssd from day_All_All_All ORDER BY date ASC"

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

        for index, row in df.iterrows():
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
            print(f'HRV for {key}')
            if key == "day_All_All_All":
                continue
            min_max = self.__conn.cursor().execute(f'SELECT min(date), max(date) FROM {key}').fetchall()
            filtered_df = df.loc[(df['date'] >= min_max[0][0]) & (df['date'] <= min_max[0][1])]
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
    def rationalApproximation(cls, t):
        # Abramowitz and Stegun formula 26.2.23.
        # The absolute value of the error should be less than 4.5 e-4.
        c = [2.515517, 0.802853, 0.010328]
        d = [1.432788, 0.189269, 0.001308]
        return t - ((c[2]*t + c[1])*t + c[0]) / (((d[2]*t + d[1])*t + d[0])*t + 1.0)

    # Implementation from https://www.johndcook.com/blog/csharp_phi_inverse/
    # this takes a percentile (probability) and returns number of SD from mean
    @classmethod
    def normalCDFInverse(cls, p):
        if p <= 0.0 or p >= 1.0:
            print("Invalid input argument: \(p)")

        # See article above for explanation of this section.
        if p < 0.5:
            # F^-1(p) = - G^-1(p)
            return -cls.rationalApproximation(np.sqrt(-2.0*np.log(p)) )
        else:
            # F^-1(p) = G^-1(1-p)
            return cls.rationalApproximation(np.sqrt(-2.0*np.log(1.0 - p)) )
