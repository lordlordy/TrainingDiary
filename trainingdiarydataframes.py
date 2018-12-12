import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
import sqlite3
import json
import logging

#specify some global constants
DAYS_DF = 'Days'
RAW_WORKOUTS_DF = 'Raw Workouts'
WORKOUTS_DF = 'Workouts'
DAY_TIMESERIES_DF = 'Date Time Series'
WEIGHTS_DF = 'Weights'
FAT_PERCENT_DF = 'FatPercent'
HR_DF = 'HR'
HRV_DF = 'HRV'

DF_DATE = 'date'
DF_WORKOUT_NUMBER = 'workoutNumber'
DF_ACTIVITY = 'activity'
DF_ACTIVITY_TYPE = 'activityType'
DF_EQUIPMENT = 'equipment'
DF_ALL = 'All'
DF_SECONDS = 'seconds'
DF_HOURS = 'hours'
DF_MINUTES = 'minutes'
DF_WEIGHTED_MEAN = 'All Wgtd Mean'
DF_TSS = 'tss'
DF_CTL = 'ctl'
DF_ATL = 'atl'
DF_TSB = 'tsb'
DF_FAT_PERCENT = 'fatPercent'
DF_KG = 'kg'
DF_LBS = 'lbs'
DF_RMSSD = 'rmssd'
DF_SDNN = 'sdnn'
DF_AGG = 'agg'
DF_MEAN = 'mean'
DF_UNIT = 'unit'
DF_SUM = 'sum'
DF_COUNT = 'count'
DF_KM = 'km'
DF_MILES = 'miles'
DF_ASCENT_METRES = 'ascentMetres'
DF_ASCENT_FEET = 'ascentFeet'
DF_SLEEP_QUALITY = 'sleepQuality'
DF_TYPE = 'type'

JSON_DAYS = 'days'
JSON_ISODATE = 'iso8061DateString'
JSON_COMMENTS = 'comments'
JSON_WORKOUTS = 'workouts'
JSON_WEIGHTS = 'weights'
JSON_PHYSIOS = 'physiologicals'
JSON_RMSSD = 'restingRMSSD'
JSON_SDNN = 'restingSDNN'
JSON_HR = 'restingHR'
JSON_ACTIVITY = 'activityString'
JSON_ACTIVITY_TYPE = 'activityTypeString'
JSON_EQUIPMENT = 'equipmentName'

PERIOD_TYPE_STD = 'STD'
PERIOD_TYPE_GROUPBY = 'groupby'
PERIOD_TYPE_ROLLING = 'rolling'
PERIOD_TYPE_TODATE = 'toDate'

LBS_PER_KG = 2.20462
FEET_PER_METRE = 3.28084
MILES_PER_KM = 0.621371

class TDDataFrames(ABC):

    def __init__(self, caching_on=True):
        self._df_dict = {}
        self._caching_on = caching_on
        self.__create_period_mapping()
        pd.options.display.float_format = '{:,.01f}'.format

    def get_units(self):
        return self.get_days_time_series_df().columns.get_level_values(0)


    def get_activities(self):
        return self.get_days_time_series_df().columns.get_level_values(1)

    # DF with single datetime index
    @abstractmethod
    def get_days_df(self):
        pass

    # DF with single datetime index
    @abstractmethod
    def get_raw_workouts_df(self):
        pass

    def get_workouts_df(self):
        if WORKOUTS_DF not in self._df_dict:
            workouts = self.get_raw_workouts_df()
            if DF_SECONDS in workouts.columns:
                workouts[DF_MINUTES] = np.around(workouts[DF_SECONDS] / 60, decimals=2)
                workouts[DF_HOURS] = np.around(workouts[DF_SECONDS] / 3600, decimals=2)
            if DF_ASCENT_METRES in workouts.columns:
                workouts[DF_ASCENT_FEET] = np.around(workouts[DF_ASCENT_METRES] * FEET_PER_METRE, decimals=2)
            if DF_KM in workouts.columns:
                workouts[DF_MILES] = np.around(workouts[DF_KM] * MILES_PER_KM, decimals=2)
                self._df_dict[WORKOUTS_DF] = workouts
        return self._df_dict[WORKOUTS_DF]

    def get_days_time_series_df(self, activity_type=None, equipment=None, drop_non_numeric=True):
        key = DAY_TIMESERIES_DF + self.__key_for(activity_type, equipment) + str(drop_non_numeric)
        logging.info(f'Key for days time series: {key}')

        if key not in self._df_dict:
            dayDF = self.__create_day_time_series(activity_type, equipment)
            if drop_non_numeric:
                dayDF.drop(['comments', 'sleepQuality', 'type'], axis=1, level=0, inplace=True)
            self._df_dict[key] = dayDF
            # if (activity_type is None) and (equipment is None):
            #     dayDF  = self.__create_day_time_series(activity_type, equipment)
            #     if drop_none_numeric:
            #         dayDF.drop(['comments', 'sleepQuality', 'type'], axis=1, level=0, inplace=True)
            #     self._df_dict[key] = dayDF
            # else:
            #     self._df_dict[key] = self.__workouts_day_time_series(activity_type, equipment)

        return self._df_dict[key]

    def __key_for(self, activity_type, equipment):
        key = ''
        if activity_type is not None:
            key += ' :' + activity_type
        if equipment is not None:
            key += ' :' + equipment
        return key

    # DF with single datetime index
    @abstractmethod
    def get_weights_df(self):
        pass

    @abstractmethod
    def get_fat_percentage_df(self):
        pass

    # DF with single datetime index
    @abstractmethod
    def get_hr_df(self):
        pass

    # DF with single datetime index
    @abstractmethod
    def get_hrv_df(self):
        pass

    def get_series(self, unit, activity, period, workout_aggregator='sum', period_aggregator='sum',
                   activity_type=None, equipment=None):

        key = self.__key_for(activity_type, equipment)
        df = self.get_days_time_series_df(activity_type, equipment)
        logging.info(f'DF series is in is of length: {len(df)}')
        logging.info(f'DF size : {df.size}')

        if df.size == 0:
            return None

        if period[0] == 'R':
            try:
                days = int(period[1:])
                print(f'Rolling {days} days')
                period_details = (PERIOD_TYPE_ROLLING, days)
            except:
                period_details = self.period_mapping[period.upper()]
        else:
            period_details = self.period_mapping[period.upper()]

        if period_details[0] == PERIOD_TYPE_STD:
            pass  # df needs no adjustment
        elif period_details[0] == PERIOD_TYPE_GROUPBY:
            if period_aggregator == DF_SUM:
                df = self.__summary_sum(df, period_details[1], key)
            elif period_aggregator == DF_MEAN:
                df = self.__summary_mean(df, period_details[1], key)
            else:
                raise Exception(f'Invalid periodAgregator {period_aggregator}')
        elif period_details[0] == PERIOD_TYPE_ROLLING:
            if period_aggregator == DF_SUM:
                df = self.__rolling_sum(df, period_details[1], key)
            elif period_aggregator == DF_MEAN:
                df = self.__rolling_mean(df, period_details[1], key)
            else:
                raise Exception(f'Invalid periodAggregator {period_aggregator}')
        elif period_details[0] == PERIOD_TYPE_TODATE:
            if period_aggregator == DF_SUM:
                df = self.__to_date_sum(df, period_details[1], key)
            elif period_aggregator == DF_MEAN:
                df = self.__to_date_mean(df, period_details[1], key)
            else:
                raise Exception(f'Invalid periodAggregator {period_aggregator}')
        else:
            raise Exception(f'Invalid period type {period}')

        if isinstance(df.index, pd.MultiIndex):
            # set index to just be datetime index (ie level 1)
            df = df.set_index(df.index.levels[0])


        return df[unit, activity, workout_aggregator]


    def units(self):
        return set(self.get_days_time_series_df().columns.get_level_values(0))

    def activities(self):
        return set(self.get_days_time_series_df().columns.get_level_values(1))

    def workout_aggregators(self):
        return set(self.get_days_time_series_df().columns.get_level_values(2))

    def __summary_sum(self, df, freq='A', key=''):
        k = f'Annual Sum {freq + key}'
        if k not in self._df_dict:
            self._df_dict[k] = df.groupby(pd.Grouper(freq=freq, level=0)).sum()
        return self._df_dict[k]

    def __summary_mean(self, df, freq='A', key=''):
        k = f'Annual Mean {freq + key}'
        if k not in self._df_dict:
            self._df_dict[k] = df.groupby(pd.Grouper(freq=freq, level=0)).mean()
        return self._df_dict[k]

    def __to_date_sum(self, df, freq='A', key=''):
        k = f'To Date Sum {freq + key}'
        if k not in self._df_dict:
            self._df_dict[k] = df.groupby(pd.Grouper(freq=freq, level=0)).cumsum()
        return self._df_dict[k]

    def __to_date_mean(self, df, freq='A', key=''):
        k = f'To Date Mean {freq + key}'
        if k not in self._df_dict:
            this_df = df.groupby(pd.Grouper(freq=freq, level=0)).expanding(1).mean()
            # expanding inserts an extra index to represent the frequency. We don't want it so remove it
            this_df.reset_index(level=0, drop=True, inplace=True)
            self._df_dict[k] = this_df
        return self._df_dict[k]

    def __rolling_sum(self, df, days, key=''):
        k = f'Rolling Sum {str(days) + key}'
        if k not in self._df_dict:
            self._df_dict[k] = df.rolling(days, min_periods=1).sum()
        return self._df_dict[k]

    def __rolling_mean(self, df, days, key=''):
        k = f'Rolling Mean {str(days)+ key}'
        if k not in self._df_dict:
            self._df_dict[k] = df.rolling(days, min_periods=1).mean()
        return self._df_dict[k]

    def __create_period_mapping(self):
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

        self.period_mapping = {'DAY': (PERIOD_TYPE_STD, 'D'), 'WEEK': (PERIOD_TYPE_GROUPBY, 'W'),
                                'MONTH': (PERIOD_TYPE_GROUPBY, 'M'), 'QUARTER': (PERIOD_TYPE_GROUPBY, 'Q'),
                                'YEAR': (PERIOD_TYPE_GROUPBY, 'A'), 'RWEEK': (PERIOD_TYPE_ROLLING, 7),
                                'RMONTH': (PERIOD_TYPE_ROLLING, 30), 'RQUARTER': (PERIOD_TYPE_ROLLING, 91),
                                'RYEAR': (PERIOD_TYPE_ROLLING, 365), 'WTD': (PERIOD_TYPE_TODATE, 'W'),
                                'MTD': (PERIOD_TYPE_TODATE, 'M'), 'QTD': (PERIOD_TYPE_TODATE, 'Q'),
                                'YTD': (PERIOD_TYPE_TODATE, 'A')}
        for m in months:
            self.period_mapping['Q-' + m] = (PERIOD_TYPE_GROUPBY, 'Q-' + m)
            self.period_mapping['Y-' + m] = (PERIOD_TYPE_GROUPBY, 'A-' + m)
            self.period_mapping['QTD-' + m] = (PERIOD_TYPE_TODATE, 'Q-' + m)
            self.period_mapping['YTD-' + m] = (PERIOD_TYPE_TODATE, 'A-' + m)

        for d in days:
            self.period_mapping['W-' + d] = (PERIOD_TYPE_GROUPBY, 'W-' + d)
            self.period_mapping['WTD-' + d] = (PERIOD_TYPE_TODATE, 'W-' + d)

        self.periods = list(self.period_mapping.keys())

    def __get_common_daily_index(self):
        days = self.get_days_df()
        days = days.set_index([DF_TYPE, DF_SLEEP_QUALITY], append=True)
        return days.index

    def __create_day_time_series(self, activity_type=None, equipment=None):

        days = self.__non_workouts_day_time_series()
        workouts = self.__workouts_day_time_series(activity_type, equipment)
        allDF = pd.concat([days, workouts], axis=1)

        allDF.rename_axis([DF_UNIT, DF_ACTIVITY, DF_AGG], axis=1, inplace=True)
        allDF.sort_index(axis=1, inplace=True)

        return allDF

    def __non_workouts_day_time_series(self):
        days = self.get_days_df()
        weights = self.get_weights_df()
        fat_p = self.get_fat_percentage_df()
        hr = self.get_hr_df()
        hrv = self.get_hrv_df()

        days[DF_ACTIVITY] = DF_ALL
        days[DF_AGG] = DF_MEAN
        # days = days.set_index([DF_ACTIVITY, DF_AGG], append=True)
        days = days.set_index([DF_TYPE, DF_SLEEP_QUALITY, DF_ACTIVITY, DF_AGG], append=True)
        days = days.unstack(level=[3,4], fill_value=0)

        # common_index = self.__get_date_index()
        common_index = days.index

        fat_p[DF_ACTIVITY] = DF_ALL
        fat_p[DF_AGG] = DF_MEAN
        fat_p = fat_p.set_index([DF_ACTIVITY, DF_AGG], append=True)
        fat_p = fat_p.unstack(level=[1,2])
        fat_p = fat_p.reindex(common_index).interpolate(method='linear')

        weights[DF_ACTIVITY] = DF_ALL
        weights[DF_AGG] = DF_MEAN
        weights = weights.set_index([DF_ACTIVITY, DF_AGG], append=True)
        weights = weights.unstack(level=[1,2])
        weights = weights.reindex(common_index).interpolate(method='linear')

        hr[DF_ACTIVITY] = DF_ALL
        hr[DF_AGG] = DF_MEAN
        hr = hr.set_index([DF_ACTIVITY, DF_AGG], append=True)
        hr = hr.unstack(level=[1, 2])
        hr = hr.reindex(common_index).interpolate(method='linear')

        hrv[DF_ACTIVITY] = DF_ALL
        hrv[DF_AGG] = DF_MEAN
        hrv = hrv.set_index([DF_ACTIVITY, DF_AGG], append=True)
        hrv = hrv.unstack(level=[1, 2])
        hrv = hrv.reindex(common_index).interpolate(method='linear')

        df = pd.concat([days, weights, fat_p, hr, hrv], axis=1)

        return df

    def __workouts_day_time_series(self, activity_type=None, equipment=None):
        workouts = self.get_workouts_df()
        logging.info(f'Number of workouts: {len(workouts)}')
        if activity_type is not None:
            workouts = workouts.query(f""" activityType == '{activity_type}' """)
            logging.info(f'Number of workouts post query for activityType = {activity_type} : {len(workouts)}')
        if equipment is not None:
            workouts = workouts.query(f""" equipment == '{equipment}' """)
            logging.info(f'Number of workouts post query for equipment = {equipment} : {len(workouts)}')

        workouts = workouts.set_index([DF_ACTIVITY, DF_ACTIVITY_TYPE, DF_EQUIPMENT, DF_WORKOUT_NUMBER], append=True)
        workouts = workouts.groupby([DF_DATE, DF_ACTIVITY]).agg(['sum','mean','count'])
        workouts = workouts.unstack(level=1, fill_value=0)
        common_index = self.__get_common_daily_index()
        workouts = workouts.reindex(common_index.levels[0], fill_value=0)
        workouts = workouts.set_index(common_index)
        workouts = workouts.swaplevel(1,2,axis=1)

        # add in totals
        for c in workouts.columns.levels[0].values:
            if len(workouts[c].columns.get_level_values(0))>1:
                workouts[c, DF_ALL, DF_SUM] = 0
                workouts[c, DF_ALL, DF_COUNT] = 0
                for c2 in workouts[c].columns.levels[0].values:
                    # print(c2)
                    if c2 is not DF_ALL:
                        workouts[c, DF_ALL, DF_SUM] += workouts[c, c2, DF_SUM]
                        workouts[c, DF_ALL, DF_COUNT] += workouts[c, c2, DF_COUNT]
                        workouts[c, DF_ALL, DF_MEAN] = workouts[c, DF_ALL, DF_SUM] / workouts[c, DF_ALL, DF_COUNT]

        self.__add_tsb_to_time_series_df(workouts)

        return workouts

    def __add_tsb_to_time_series_df(self, df, ctl_decay_days=42, ctl_impact_days=42, atl_decay_days=7, atl_impact_days=7):

        tss = df[DF_TSS]

        c_decay = np.exp(-1/ctl_decay_days)
        c_impact = 1 - np.exp(-1/ctl_impact_days)
        a_decay = np.exp(-1/atl_decay_days)
        a_impact = 1 - np.exp(-1/atl_impact_days)

        for c in tss.columns.levels[0].values:
            prev_atl = prev_ctl = 0
            atl_array = []
            ctl_array = []
            tsb_array = []
            for t in tss[c, DF_SUM].values:
                ctl = t * c_impact + prev_ctl * c_decay
                atl = t * a_impact + prev_atl * a_decay
                atl_array.append(atl)
                ctl_array.append(ctl)
                tsb_array.append(ctl - atl)
                prev_ctl = ctl
                prev_atl = atl
            df[DF_CTL, c, DF_SUM] = ctl_array
            df[DF_ATL, c, DF_SUM] = atl_array
            df[DF_TSB, c, DF_SUM] = tsb_array

        df.sort_index(axis=1, inplace=True)

class TDDataFramesSQLITE(TDDataFrames):

    def __init__(self, db_url, training_diary_name):
        super().__init__()
        self.db_url = db_url
        self.td_name = training_diary_name

    def get_raw_workouts_df(self):
        df = self.__read_sql_df(f'''select * from workout where trainingDiary="{self.td_name}" ''')
        df = df.drop(['id','trainingDiary'], axis=1)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        return df

    def get_days_df(self):
        df = self.__read_sql_df(f'''select * from day where trainingDiary="{self.td_name}" ''')
        df = df.drop(['id','trainingDiary'], axis=1)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        return df

    # DF with single datetime index
    def get_weights_df(self):
        df = self.__read_sql_df(f'''select date, kg, kg*{LBS_PER_KG} as lbs from weight where trainingDiary="{self.td_name}" ''')
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        return df

    def get_fat_percentage_df(self):
        df = self.__read_sql_df(f'''select date, percentage from bodyFat where trainingDiary="{self.td_name}" ''')
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        return df

    # DF with single datetime index
    def get_hr_df(self):
        df = self.__read_sql_df(f'''select date, restingHR from hr where trainingDiary="{self.td_name}" ''')
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        return df

    # DF with single datetime index
    def get_hrv_df(self):
        df = self.__read_sql_df(f'''select date, sdnn, rmssd from hrv where trainingDiary="{self.td_name}" ''')
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        return df

    def __read_sql_df(self, sql):
        conn = sqlite3.connect(self.db_url)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df

class TDDataFramesJSON(TDDataFrames):

    def __init__(self, json_file):
        super().__init__()
        self.__dict = json.load(open(json_file))

    # DF with datetime index
    def get_days_df(self):
        if DAYS_DF not in self._df_dict:
            self._df_dict[DAYS_DF] = self.__createDays()
        return self._df_dict[DAYS_DF]

    # DF with datetime index
    def get_raw_workouts_df(self):
        if RAW_WORKOUTS_DF not in self._df_dict:
            self._df_dict[RAW_WORKOUTS_DF] = self.__createWorkouts()
        return self._df_dict[RAW_WORKOUTS_DF]

    def get_fat_percentage_df(self):
        if FAT_PERCENT_DF  not in self._df_dict:
            wdf = self.__createWeightDF()
            self._df_dict[FAT_PERCENT_DF] = wdf.drop(DF_KG, axis=1)
        return self._df_dict[FAT_PERCENT_DF]

    def get_weights_df(self):
        if WEIGHTS_DF not in self._df_dict:
            wdf = self.__createWeightDF()
            wdf[DF_LBS] = wdf[DF_KG] * LBS_PER_KG
            self._df_dict[WEIGHTS_DF] = wdf.drop(DF_FAT_PERCENT, axis=1)
        return self._df_dict[WEIGHTS_DF]

    def get_hr_df(self):
        if HR_DF not in self._df_dict:
            hr = self.__createPhysiosDF()
            self._df_dict[HR_DF] = hr.drop([DF_SDNN, DF_RMSSD], axis=1)
        return self._df_dict[HR_DF]

    def get_hrv_df(self):
        if HRV_DF not in self._df_dict:
            hr = self.__createPhysiosDF()
            self._df_dict[HRV_DF] = hr.drop(JSON_HR, axis=1)
        return self._df_dict[HRV_DF]

    def __createDays(self):
        days = self.__dict[JSON_DAYS]
        df = pd.DataFrame(days)
        df[DF_DATE] = pd.to_datetime(df[JSON_ISODATE])
        df.set_index([pd.DatetimeIndex(df[DF_DATE]).floor('1D')], inplace=True)
        df.drop([JSON_WORKOUTS, JSON_ISODATE, DF_DATE], axis=1, inplace=True)
        return df

    def __createWorkouts(self):
        data_dict = {}

        for d in self.__dict[JSON_DAYS]:
            date = pd.to_datetime(d[JSON_ISODATE])

            # check for workouts
            if JSON_WORKOUTS in d and len(d[JSON_WORKOUTS]) > 0:
                # count = 0
                count_dict = {}
                for w in d[JSON_WORKOUTS]:
                    key = w[JSON_ACTIVITY] + w[JSON_ACTIVITY_TYPE] + w[JSON_EQUIPMENT]
                    count = count_dict.get(key,0)
                    count += 1
                    count_dict[key] = count
                    array = data_dict.get(DF_WORKOUT_NUMBER, [])
                    array.append(count)
                    data_dict[DF_WORKOUT_NUMBER] = array
                    array = data_dict.get(DF_DATE, [])
                    array.append(date)
                    data_dict[DF_DATE] = array
                    for key, value in w.items():
                        array = data_dict.get(key, [])
                        array.append(value)
                        data_dict[key] = array

        df = pd.DataFrame(data_dict)
        df.set_index([pd.DatetimeIndex(df[DF_DATE]).floor('1D')], inplace=True)
        df.drop([DF_DATE], axis=1, inplace=True)
        df.rename(index=str, columns={JSON_ACTIVITY: DF_ACTIVITY, JSON_ACTIVITY_TYPE: DF_ACTIVITY_TYPE, JSON_EQUIPMENT: DF_EQUIPMENT}, inplace=True)
        return df

    def __createWeightDF(self):
        weights = self.__dict[JSON_WEIGHTS]
        df = pd.DataFrame(weights)
        df[DF_DATE] = pd.to_datetime(df[JSON_ISODATE])
        df.set_index([pd.DatetimeIndex(df[DF_DATE]).floor('1D')], inplace=True)
        df.drop([JSON_ISODATE, DF_DATE], axis=1, inplace=True)
        return df

    def __createPhysiosDF(self):
        physios = self.__dict[JSON_PHYSIOS]
        df = pd.DataFrame(physios)
        df[DF_DATE] = pd.to_datetime(df[JSON_ISODATE])
        df.set_index([pd.DatetimeIndex(df[DF_DATE]).floor('1D')], inplace=True)
        df.drop([JSON_ISODATE, DF_DATE], axis=1, inplace=True)
        df.rename(index=str, columns={JSON_RMSSD: DF_RMSSD, JSON_SDNN: DF_SDNN}, inplace=True)
        return df


if __name__ == '__main__':
    import logging

    # f = open('TrainingDiary.json')
    # data = json.load(f)

    formatStr = '%(asctime)s %(levelname)s: %(filename)s %(funcName)s Line:%(lineno)d %(message)s'
    dateFormatStr = '%Y-%b-%d %H:%M:%S'

    # logging.basicConfig(filename='TrainingDiary.log',
    #                     filemode='w',
    #                     level=logging.DEBUG,
    #                     format=formatStr,
    #                     datefmt=dateFormatStr)

    logging.basicConfig(level=logging.DEBUG,
                        format=formatStr,
                        datefmt=dateFormatStr)
    import Eddington

    df = TDDataFramesSQLITE('TD.db', 'StevenLordDiary')
    bikeMiles = df.get_series('km', 'Bike', 'Day')
    e = Eddington.eddingtonHistoryDF(bikeMiles)

    # df = data_frames.get_days_time_series_df(drop_non_numeric=False)
    # logging.info(type(df))
    # df = dataFrames.getSeries('km','Bike','Year','sum','sum','Turbo','IF XS')
    # df = dataFrames.getSeries('km','Run','Year','sum','sum','Road')
    # df = dataFrames.getSeries('km','Swim','Year','sum','sum','Squad')

