import pandas as pd
import numpy as np
import datetime

#specify some global constants
DAYS_DF = 'Days'
WORKOUTS_DF = 'Workouts'
DAY_TIMESERIES_DF = 'Date Time Series'
WEIGHTS_DF = 'Weights'
PHYSIOS_DF = 'Physios'

DF_DATE = 'date'
DF_WORKOUT_NUMBER = 'workout #'
DF_ACTIVITY = 'activityString'
DF_ACTIVITY_TYPE = 'activityTypeString'
DF_EQUIPMENT = 'equipmentName'
DF_TOTAL = 'total'
DF_SECONDS = 'seconds'
DF_HOURS = 'hours'
DF_WEIGHTED_MEAN = 'Weighted Mean'
DF_TSS = 'tss'
DF_CTL = 'ctl'
DF_ATL = 'atl'
DF_TSB = 'tsb'

JSON_DAYS = 'days'
JSON_ISODATE = 'iso8061DateString'
JSON_COMMENTS = 'comments'
JSON_WORKOUTS = 'workouts'
JSON_WEIGHTS = 'weights'
JSON_PHYSIOS = 'physiologicals'


class TDDataFrames:

    def __init__(self, trainingDiaryJSONDict):
        self.__dict = trainingDiaryJSONDict
        self.__dfDict = {}

    def getDaysDF(self):
        if DAYS_DF not in self.__dfDict:
            self.__dfDict[DAYS_DF] = self.__createDays()
        return self.__dfDict[DAYS_DF]

    def getWorkoutsDF(self):
        if WORKOUTS_DF not in self.__dfDict:
            self.__dfDict[WORKOUTS_DF] = self.__createWorkouts()
        return self.__dfDict[WORKOUTS_DF]

    def getDaysTimeSeriesDF(self):
        if DAY_TIMESERIES_DF not in self.__dfDict:
            self.__dfDict[DAY_TIMESERIES_DF] = self.__createDayTimeSeries()
        return self.__dfDict[DAY_TIMESERIES_DF]

    def getWeightsDF(self):
        if WEIGHTS_DF not in self.__dfDict:
            self.__dfDict[WEIGHTS_DF] = self.__createWeightDF()
        return self.__dfDict[WEIGHTS_DF]

    def getPhysiosDF(self):
        if PHYSIOS_DF not in self.__dfDict:
            self.__dfDict[PHYSIOS_DF] = self.__createPhysiosDF()
        return self.__dfDict[PHYSIOS_DF]

    def addTSBToTimeSeriesDF(self, ctlDecayDays=42, ctlImpactDays=42, atlDecayDays=7, atlImpactDays=7):

        df = self.getDaysTimeSeriesDF()
        tss = df[DF_TSS]

        cDecay = np.exp(-1/ctlDecayDays)
        cImpact = 1 - np.exp(-1/ctlImpactDays)
        aDecay = np.exp(-1/atlDecayDays)
        aImpact = 1 - np.exp(-1/atlImpactDays)

        for c in tss.columns.values:
            prevATL = prevCTL = 0
            atlArray = []
            ctlArray = []
            tsbArray = []
            # temp = tss[c]
            # v = temp.values
            for t in tss[c].values:
                ctl = t * cImpact + prevCTL * cDecay
                atl = t * aImpact + prevATL * aDecay
                atlArray.append(atl)
                ctlArray.append(ctl)
                tsbArray.append(ctl - atl)
                prevCTL = ctl
                prevATL = atl
            df[DF_CTL, c] = ctlArray
            df[DF_ATL, c] = atlArray
            df[DF_TSB, c] = tsbArray

    def __createDayTimeSeries(self):
        days = self.getDaysDF()
        workouts = self.getWorkoutsDF()
        weights = self.getWeightsDF()
        physios = self.getPhysiosDF()

        maxDate = days.index.max()
        minDate = days.index.min()

        days['All'] = 'All'
        days = days.set_index(['All'], append=True)
        days = days.unstack(level=1, fill_value=0)

        datesIndex = pd.date_range(minDate, maxDate, freq='D')

        workouts = workouts.unstack(level=1, fill_value=0).groupby([DF_DATE]).sum()
        workouts = workouts.reindex(datesIndex, fill_value=0)

        weights['All'] = 'All'
        weights = weights.set_index(['All'], append=True)
        weights = weights.unstack(level=1)
        weights = weights.reindex(datesIndex).interpolate(method='linear')

        physios['All'] = 'All'
        physios = physios.set_index(['All'], append=True)
        physios = physios.unstack(level=1)
        physios = physios.reindex(datesIndex).interpolate(method='linear')

        allDF = pd.concat([days, workouts, weights, physios], axis=1)

        # add in totals
        for c in allDF.columns.levels[0].values:
            if len(allDF[c].columns.values)>1:
                allDF[c, DF_TOTAL] = 0
                for c2 in allDF[c].columns.values:
                    if c2 is not DF_TOTAL:
                        allDF[c,DF_TOTAL] += allDF[c,c2]

        # add hours
        if DF_SECONDS in allDF.columns.levels[0].values:
            for c in allDF[DF_SECONDS].columns:
                allDF[DF_HOURS,c] = np.around(allDF[DF_SECONDS,c]/3600, decimals=2)
            # add weighted mean - weighted on seconds
            for c in allDF.columns.levels[0].values:
                if len(allDF[c].columns.values)>1:
                    allDF[c,'Weighted'] = 0
                    for c2 in allDF[c].columns.values:
                        if (c2 is not DF_TOTAL) and (c2 is not 'Weighted'):
                            allDF[c,'Weighted'] += allDF[DF_SECONDS,c2]*allDF[c,c2]
                    allDF[c, DF_WEIGHTED_MEAN] = np.around(allDF[c,'Weighted'] / allDF[DF_SECONDS, DF_TOTAL], decimals=2)
                    allDF[c, DF_WEIGHTED_MEAN] = allDF[c, DF_WEIGHTED_MEAN].fillna(0)

        allDF = allDF.drop('Weighted', axis=1, level=1)

        return allDF

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
                count = 0
                for w in d[JSON_WORKOUTS]:
                    count += 1
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
        df.set_index([pd.DatetimeIndex(df[DF_DATE]).floor('1D'), DF_ACTIVITY,
                      DF_ACTIVITY_TYPE, DF_EQUIPMENT,
                      DF_WORKOUT_NUMBER], inplace=True)
        df.drop([DF_DATE], axis=1, inplace=True)
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
        return df


if __name__ == '__main__':
    import json
    f = open('TrainingDiary.json')
    data = json.load(f)
    dataFrames = TDDataFrames(data)
    df = dataFrames.getDaysTimeSeriesDF()
    dataFrames.addTSBToTimeSeriesDF()

