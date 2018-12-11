import pandas as pd
import numpy as np
import datetime
from abc import ABC, abstractmethod
import sqlite3
import json
import logging

#specify some global constants
DAYS_DF = 'Days'
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

    def __init__(self, cachingOn=True):
        self._dfDict = {}
        self._cachingOn = cachingOn
        self.__createPeriodMapping()
        pd.options.display.float_format = '{:,.01f}'.format

    def getUnits(self):
        return self.getDaysTimeSeriesDF().columns.get_level_values(0)


    def getActivities(self):
        return self.getDaysTimeSeriesDF().columns.get_level_values(1)

    # DF with single datetime index
    @abstractmethod
    def getDaysDF(self):
        pass

    # DF with single datetime index
    @abstractmethod
    def getWorkoutsDF(self):
        pass

    def getDaysTimeSeriesDF(self):
        if DAY_TIMESERIES_DF not in self._dfDict:
            self._dfDict[DAY_TIMESERIES_DF] = self.__createDayTimeSeries()
        return self._dfDict[DAY_TIMESERIES_DF]

    # DF with single datetime index
    @abstractmethod
    def getWeightsDF(self):
        pass

    @abstractmethod
    def getFatPercentageDF(self):
        pass

    # DF with single datetime index
    @abstractmethod
    def getHRDF(self):
        pass

    # DF with single datetime index
    @abstractmethod
    def getHRVDF(self):
        pass

    def getSeries(self, unit, activity, period, workoutAggregator, periodAggregator):

        if period[0] == 'R':
            try:
                days = int(period[1:])
                print(f'Rolling {days} days')
                periodDetails = (PERIOD_TYPE_ROLLING, days)
            except:
                periodDetails = self.periodMapping[period]
        else:
            periodDetails = self.periodMapping[period]

        if periodDetails[0] == PERIOD_TYPE_STD:
            df = self.getDaysTimeSeriesDF()
        elif periodDetails[0] == PERIOD_TYPE_GROUPBY:
            if periodAggregator == DF_SUM:
                df = self.summarySum(periodDetails[1])
            elif periodAggregator == DF_MEAN:
                df = self.summaryMean(periodDetails[1])
            else:
                raise Exception(f'Invalid periodAgregator {periodAggregator}')
        elif periodDetails[0] == PERIOD_TYPE_ROLLING:
            if periodAggregator == DF_SUM:
                df = self.rollingSum(periodDetails[1])
            elif periodAggregator == DF_MEAN:
                df = self.rollingMean(periodDetails[1])
            else:
                raise Exception(f'Invalid periodAggregator {periodAggregator}')
        elif periodDetails[0] == PERIOD_TYPE_TODATE:
            if periodAggregator == DF_SUM:
                df = self.toDateSum(periodDetails[1])
            elif periodAggregator == DF_MEAN:
                df = self.toDateMean(periodDetails[1])
            else:
                raise Exception(f'Invalid periodAggregator {periodAggregator}')
        else:
            raise Exception(f'Invalid period type {period}')

        return df[unit, activity, workoutAggregator]


    def units(self):
        return set(self.getDaysTimeSeriesDF().columns.get_level_values(0))

    def activities(self):
        return set(self.getDaysTimeSeriesDF().columns.get_level_values(1))

    def workoutAggregators(self):
        return set(self.getDaysTimeSeriesDF().columns.get_level_values(2))


    def summarySum(self, freq='A'):
        key = f'Annual Sum {freq}'
        if key not in self._dfDict:
            self._dfDict[key] = self.getDaysTimeSeriesDF().groupby(pd.Grouper(freq=freq)).sum()
        return self._dfDict[key]

    def summaryMean(self, freq='A'):
        key = f'Annual Mean {freq}'
        if key not in self._dfDict:
            self._dfDict[key] = self.getDaysTimeSeriesDF().groupby(pd.Grouper(freq=freq)).mean()
        return self._dfDict[key]

    def toDateSum(self, freq='A'):
        key = f'To Date Sum {freq}'
        if key not in self._dfDict:
            self._dfDict[key] = self.getDaysTimeSeriesDF().groupby(pd.Grouper(freq=freq)).cumsum()
        return self._dfDict[key]

    def toDateMean(self, freq='A'):
        key = f'To Date Mean {freq}'
        if key not in self._dfDict:
            df = self.getDaysTimeSeriesDF().groupby(pd.Grouper(freq=freq)).expanding(1).mean()
            # expanding inserts an extra index to represent the frequency. We don't want it so remove it
            df.reset_index(level=0, drop=True, inplace=True)
            self._dfDict[key] = df
        return self._dfDict[key]

    def rollingSum(self, days):
        key = f'Rolling Sum {str(days)}'
        if key not in self._dfDict:
            self._dfDict[key] = self.getDaysTimeSeriesDF().rolling(days, min_periods=1).sum()
        return self._dfDict[key]

    def rollingMean(self, days):
        key = f'Rolling Mean {str(days)}'
        if key not in self._dfDict:
            self._dfDict[key] = self.getDaysTimeSeriesDF().rolling(days, min_periods=1).mean()
        return self._dfDict[key]

    def __createPeriodMapping(self):
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        rolling = ['RWeek', 'RMonth', 'RYear', 'RInteger']
        toDate = ['WTD-' + i for i in days] + ['YTD-' + i for i in months] + ['WTD', 'MTD', 'YTD']
        stdDaily = ['Day']
        stdNonDaily = ['W-' + i for i in days] + ['Y-' + i for i in months] + ['Q-' + i for i in months]

        self.periodMapping = {'Day': (PERIOD_TYPE_STD,'D'), 'Week': (PERIOD_TYPE_GROUPBY,'W'),
                              'Month': (PERIOD_TYPE_GROUPBY,'M'), 'Quarter': (PERIOD_TYPE_GROUPBY,'Q'),
                              'Year': (PERIOD_TYPE_GROUPBY,'A'), 'RWeek': (PERIOD_TYPE_ROLLING,7),
                              'RMonth': (PERIOD_TYPE_ROLLING,30), 'RQuarter': (PERIOD_TYPE_ROLLING,91),
                              'RYear': (PERIOD_TYPE_ROLLING,365), 'WTD': (PERIOD_TYPE_TODATE, 'W'),
                              'MTD': (PERIOD_TYPE_TODATE, 'M'), 'QTD': (PERIOD_TYPE_TODATE, 'Q'),
                              'YTD': (PERIOD_TYPE_TODATE, 'A')}
        for m in months:
            self.periodMapping['Q-' + m] = (PERIOD_TYPE_GROUPBY, 'Q-' + m)
            self.periodMapping['Y-' + m] = (PERIOD_TYPE_GROUPBY, 'A-' + m)
            self.periodMapping['QTD-' + m] = (PERIOD_TYPE_TODATE, 'Q-' + m)
            self.periodMapping['YTD-' + m] = (PERIOD_TYPE_TODATE, 'A-' + m)

        for d in days:
            self.periodMapping['W-' + d] = (PERIOD_TYPE_GROUPBY, 'W-' + d)
            self.periodMapping['WTD-' + d] = (PERIOD_TYPE_TODATE, 'W-' + d)

        self.periods = list(self.periodMapping.keys())

    def __createDayTimeSeries(self):
        days = self.getDaysDF()
        workouts = self.getWorkoutsDF()
        weights = self.getWeightsDF()
        fatP = self.getFatPercentageDF()
        hr = self.getHRDF()
        hrv = self.getHRVDF()

        maxDate = days.index.max()
        minDate = days.index.min()

        days[DF_ACTIVITY] = DF_ALL
        days[DF_AGG] = DF_MEAN
        days = days.set_index([DF_ACTIVITY, DF_AGG], append=True)
        days = days.unstack(level=[1,2], fill_value=0)

        datesIndex = pd.date_range(minDate, maxDate, freq='D')

        workouts = workouts.set_index([DF_ACTIVITY, DF_ACTIVITY_TYPE, DF_EQUIPMENT, DF_WORKOUT_NUMBER], append=True)
        workouts = workouts.groupby([DF_DATE, DF_ACTIVITY]).agg(['sum','mean','count'])
        workouts = workouts.unstack(level=1, fill_value=0)
        workouts = workouts.reindex(datesIndex, fill_value=0)
        workouts = workouts.swaplevel(1,2,axis=1)

        fatP[DF_ACTIVITY] = DF_ALL
        fatP[DF_AGG] = DF_MEAN
        fatP = fatP.set_index([DF_ACTIVITY, DF_AGG], append=True)
        fatP = fatP.unstack(level=[1,2])
        fatP = fatP.reindex(datesIndex).interpolate(method='linear')

        weights[DF_ACTIVITY] = DF_ALL
        weights[DF_AGG] = DF_MEAN
        weights = weights.set_index([DF_ACTIVITY, DF_AGG], append=True)
        weights = weights.unstack(level=[1,2])
        weights = weights.reindex(datesIndex).interpolate(method='linear')

        hr[DF_ACTIVITY] = DF_ALL
        hr[DF_AGG] = DF_MEAN
        hr = hr.set_index([DF_ACTIVITY,DF_AGG], append=True)
        hr = hr.unstack(level=[1,2])
        hr = hr.reindex(datesIndex).interpolate(method='linear')

        hrv[DF_ACTIVITY] = DF_ALL
        hrv[DF_AGG] = DF_MEAN
        hrv = hrv.set_index([DF_ACTIVITY,DF_AGG], append=True)
        hrv = hrv.unstack(level=[1,2])
        hrv = hrv.reindex(datesIndex).interpolate(method='linear')

        allDF = pd.concat([days, workouts, weights, fatP, hr, hrv], axis=1)

        logging.info(days.columns)
        logging.info(workouts.columns)
        logging.info(fatP.columns)
        logging.info(weights.columns)
        logging.info(hr.columns)
        logging.info(hrv.columns)
        logging.info(allDF.columns)

        # add in totals
        for c in allDF.columns.levels[0].values:
            # print(c)
            # print(allDF[c].columns.get_level_values(0))
            if len(allDF[c].columns.get_level_values(0))>1:
                allDF[c, DF_ALL, DF_SUM] = 0
                allDF[c, DF_ALL, DF_COUNT] = 0
                for c2 in allDF[c].columns.levels[0].values:
                    # print(c2)
                    if c2 is not DF_ALL:
                        allDF[c, DF_ALL, DF_SUM] += allDF[c, c2, DF_SUM]
                        allDF[c, DF_ALL, DF_COUNT] += allDF[c, c2, DF_COUNT]
                allDF[c, DF_ALL, DF_MEAN] = allDF[c, DF_ALL, DF_SUM] / allDF[c, DF_ALL, DF_COUNT]

        # add hours
        if DF_SECONDS in allDF.columns.levels[0].values:
            for c in allDF[DF_SECONDS].columns.levels[0].values:
                allDF[DF_HOURS,c, DF_SUM] = np.around(allDF[DF_SECONDS,c, DF_SUM]/3600, decimals=2)
                allDF[DF_HOURS,c, DF_MEAN] = np.around(allDF[DF_SECONDS,c, DF_MEAN]/3600, decimals=2)
                allDF[DF_HOURS,c, DF_COUNT] = allDF[DF_SECONDS,c, DF_COUNT]

        # add miles
        if DF_KM in allDF.columns.levels[0].values:
            for c in allDF[DF_KM].columns.levels[0].values:
                allDF[DF_MILES,c, DF_SUM] = np.around(allDF[DF_KM,c, DF_SUM]*MILES_PER_KM, decimals=2)
                allDF[DF_MILES,c, DF_MEAN] = np.around(allDF[DF_KM,c, DF_MEAN]*MILES_PER_KM, decimals=2)
                allDF[DF_MILES,c, DF_COUNT] = allDF[DF_KM,c, DF_COUNT]

        # add feet
        if DF_ASCENT_METRES in allDF.columns.levels[0].values:
            for c in allDF[DF_ASCENT_METRES].columns.levels[0].values:
                allDF[DF_ASCENT_FEET,c, DF_SUM] = np.around(allDF[DF_ASCENT_METRES,c, DF_SUM]*FEET_PER_METRE, decimals=2)
                allDF[DF_ASCENT_FEET,c, DF_MEAN] = np.around(allDF[DF_ASCENT_METRES,c, DF_MEAN]*FEET_PER_METRE, decimals=2)
                allDF[DF_ASCENT_FEET,c, DF_COUNT] = allDF[DF_ASCENT_METRES,c, DF_COUNT]

        allDF.rename_axis([DF_UNIT, DF_ACTIVITY, DF_AGG], axis=1, inplace=True)

        allDF.drop(['comments','sleepQuality','type'], axis=1, level=0, inplace=True)


        allDF.sort_index(axis=1, inplace=True)

        self.__addTSBToTimeSeriesDF(allDF)

        return allDF

    def __addTSBToTimeSeriesDF(self, df, ctlDecayDays=42, ctlImpactDays=42, atlDecayDays=7, atlImpactDays=7):

        tss = df[DF_TSS]

        cDecay = np.exp(-1/ctlDecayDays)
        cImpact = 1 - np.exp(-1/ctlImpactDays)
        aDecay = np.exp(-1/atlDecayDays)
        aImpact = 1 - np.exp(-1/atlImpactDays)

        for c in tss.columns.levels[0].values:
            prevATL = prevCTL = 0
            atlArray = []
            ctlArray = []
            tsbArray = []
            # temp = tss[c]
            # v = temp.values
            for t in tss[c, DF_SUM].values:
                ctl = t * cImpact + prevCTL * cDecay
                atl = t * aImpact + prevATL * aDecay
                atlArray.append(atl)
                ctlArray.append(ctl)
                tsbArray.append(ctl - atl)
                prevCTL = ctl
                prevATL = atl
            df[DF_CTL, c, DF_SUM] = ctlArray
            df[DF_ATL, c, DF_SUM] = atlArray
            df[DF_TSB, c, DF_SUM] = tsbArray

        df.sort_index(axis=1, inplace=True)



class TDDataFramesSQLITE(TDDataFrames):

    def __init__(self, dbURL, trainingDiaryName):
        super().__init__()
        self.dbURL = dbURL
        self.tdName = trainingDiaryName


    def getWorkoutsDF(self):
        df = self.__readSQLDF(f'''select * from workout where trainingDiary="{self.tdName}" ''')
        df = df.drop(['id','trainingDiary'], axis=1)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        return df

    def getDaysDF(self):
        df = self.__readSQLDF(f'''select * from day where trainingDiary="{self.tdName}" ''')
        df = df.drop(['id','trainingDiary'], axis=1)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        return df

    # DF with single datetime index
    def getWeightsDF(self):
        df = self.__readSQLDF(f'''select date, kg, kg*{LBS_PER_KG} as lbs from weight where trainingDiary="{self.tdName}" ''')
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        return df

    def getFatPercentageDF(self):
        df = self.__readSQLDF(f'''select date, percentage from bodyFat where trainingDiary="{self.tdName}" ''')
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        return df

    # DF with single datetime index
    def getHRDF(self):
        df = self.__readSQLDF(f'''select date, restingHR from hr where trainingDiary="{self.tdName}" ''')
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        return df

    # DF with single datetime index
    def getHRVDF(self):
        df = self.__readSQLDF(f'''select date, sdnn, rmssd from hrv where trainingDiary="{self.tdName}" ''')
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        return df

    def __readSQLDF(self, sql):
        conn = sqlite3.connect(self.dbURL)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df

class TDDataFramesJSON(TDDataFrames):

    def __init__(self, jsonFile):
        super().__init__()
        self.__dict = json.load(open(jsonFile))

    # DF with datetime index
    def getDaysDF(self):
        if DAYS_DF not in self._dfDict:
            self._dfDict[DAYS_DF] = self.__createDays()
        return self._dfDict[DAYS_DF]

    # DF with datetime index
    def getWorkoutsDF(self):
        if WORKOUTS_DF not in self._dfDict:
            self._dfDict[WORKOUTS_DF] = self.__createWorkouts()
        return self._dfDict[WORKOUTS_DF]

    def getFatPercentageDF(self):
        if FAT_PERCENT_DF  not in self._dfDict:
            wdf = self.__createWeightDF()
            self._dfDict[FAT_PERCENT_DF] = wdf.drop(DF_KG, axis=1)
        return self._dfDict[FAT_PERCENT_DF]

    def getWeightsDF(self):
        if WEIGHTS_DF not in self._dfDict:
            wdf = self.__createWeightDF()
            wdf[DF_LBS] = wdf[DF_KG] * LBS_PER_KG
            self._dfDict[WEIGHTS_DF] = wdf.drop(DF_FAT_PERCENT, axis=1)
        return self._dfDict[WEIGHTS_DF]

    def getHRDF(self):
        if HR_DF not in self._dfDict:
            hr = self.__createPhysiosDF()
            self._dfDict[HR_DF] = hr.drop([DF_SDNN, DF_RMSSD], axis=1)
        return self._dfDict[HR_DF]

    def getHRVDF(self):
        if HRV_DF not in self._dfDict:
            hr = self.__createPhysiosDF()
            self._dfDict[HRV_DF] = hr.drop(JSON_HR, axis=1)
        return self._dfDict[HRV_DF]

    def __createDays(self):
        days = self.__dict[JSON_DAYS]
        df = pd.DataFrame(days)
        df[DF_DATE] = pd.to_datetime(df[JSON_ISODATE])
        df.set_index([pd.DatetimeIndex(df[DF_DATE]).floor('1D')], inplace=True)
        df.drop([JSON_WORKOUTS, JSON_ISODATE, DF_DATE], axis=1, inplace=True)
        return df

    def __createWorkouts(self):
        dataDict = {}

        for d in self.__dict[JSON_DAYS]:
            date = pd.to_datetime(d[JSON_ISODATE])

            # check for workouts
            if JSON_WORKOUTS in d and len(d[JSON_WORKOUTS]) > 0:
                # count = 0
                countDict = {}
                for w in d[JSON_WORKOUTS]:
                    key = w[JSON_ACTIVITY] + w[JSON_ACTIVITY_TYPE] + w[JSON_EQUIPMENT]
                    count = countDict.get(key,0)
                    count += 1
                    countDict[key] = count
                    array = dataDict.get(DF_WORKOUT_NUMBER, [])
                    array.append(count)
                    dataDict[DF_WORKOUT_NUMBER] = array
                    array = dataDict.get(DF_DATE, [])
                    array.append(date)
                    dataDict[DF_DATE] = array
                    for key, value in w.items():
                        array = dataDict.get(key, [])
                        array.append(value)
                        dataDict[key] = array

        df = pd.DataFrame(dataDict)
        df.set_index([pd.DatetimeIndex(df[DF_DATE]).floor('1D')], inplace=True)
        # df.set_index([pd.DatetimeIndex(df[DF_DATE]).floor('1D'), DF_ACTIVITY,
        #               DF_ACTIVITY_TYPE, DF_EQUIPMENT,
        #               DF_WORKOUT_NUMBER], inplace=True)
        # df.set_index([pd.DatetimeIndex(df[DF_DATE]).floor('1D'), DF_ACTIVITY,
        #               DF_ACTIVITY_TYPE, DF_EQUIPMENT], inplace=True)
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

    logging.basicConfig(filename='TrainingDiary.log',
                        filemode='w',
                        level=logging.DEBUG,
                        format=formatStr,
                        datefmt=dateFormatStr)

    dataFrames = TDDataFramesSQLITE('TD.db','StevenLordDiary')
    df = dataFrames.getDaysTimeSeriesDF()
    dataFrames.addTSBToTimeSeriesDF()

