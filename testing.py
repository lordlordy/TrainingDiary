import json
import pandas as pd
import numpy as np
import dateutil.parser
from functools import reduce
import operator
from datetime import date
import calendar

import matplotlib
# this line needed to stop it crashing when using in tkinter
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import gridspec
from matplotlib import cm


from numpy.polynomial.polynomial import polyfit
import tkinter as tk
from tkinter import filedialog


DF_DATE, DF_ACTIVITY, DF_ACTIVITY_TYPE, DF_EQUIPMENT, DF_WORKOUT = 'Date', 'Activity', 'Activity Type', 'Equipment', 'Workout #'
DF_ASCENT_METRES, DF_KJ, DF_SECONDS, DF_REPS, DF_KM, DF_TSS, DF_BRICK, DF_RPE, DF_WATTS, DF_CADENCE, DF_HR, DF_HOURS, DF_TOTAL = 'ascentMetres', 'kj', 'seconds', 'reps', 'km', 'tss', 'brick', 'rpe', 'watts', 'cadence', 'hr', 'hours', 'total'

DF_INDEX = [DF_DATE, DF_ACTIVITY, DF_ACTIVITY_TYPE, DF_EQUIPMENT, DF_WORKOUT]
DF_COLUMNS = [DF_ASCENT_METRES, DF_KJ, DF_SECONDS, DF_REPS, DF_KM, DF_TSS, DF_BRICK, DF_RPE, DF_WATTS, DF_CADENCE, DF_HR]

class PlotTest:

    def __init__(self, root=None):
        self.__root = root

    def loadAndCreateWeightDF(self):
        f = open('TrainingDiary.json', encoding="utf-8")
        data = json.load(f)
        weights = data['weights']
        dataDict = {DF_DATE:[],
                    'kg': [],
                    'fatPercent': []}
        for w in weights:
            dataDict[DF_DATE].append(dateutil.parser.parse(w['iso8061DateString']).date())
            dataDict['kg'].append(w['kg'])
            dataDict['fatPercent'].append(w['fatPercent'])

        df = pd.DataFrame(dataDict)
        # set up index as a proper date from DF_DATE column
        df = df.set_index([pd.DatetimeIndex(df[DF_DATE])])
        # remove old date column as now have a proper date based one.
        df.drop([DF_DATE],axis=1,inplace=True)
        return df

    def loadAndCreateTimeSeriesDataFrame(self):
        df = self.loadAndCreateSimpleDataFrame()
        # move activity up to column labels
        df = self._unstackActivityAndAddTotals(df)
        # group by day
        df = df.groupby([DF_DATE]).sum()
        maxDate = max(df.index.values)
        minDate = min(df.index.values)
        # re index so we include missing days - insert zeroes for them
        df = df.reindex(pd.date_range(start=minDate, end=maxDate, freq='D'), fill_value=0)
        return df

    def _unstackActivityAndAddTotals(self,df):
        withTotalsDF = df.unstack(level=1, fill_value=0)
        # inserts an hours column
        for level2 in withTotalsDF.columns.levels[1]:
            withTotalsDF['hours', level2] = withTotalsDF['seconds', level2] / 3600

        for level1 in withTotalsDF.columns.levels[0]:
            withTotalsDF[level1, 'Total'] = 0
            for level2 in withTotalsDF.columns.levels[1]: \
                    # need this check so we don't double count
                if level2 is not 'Total':
                    withTotalsDF[level1, 'Total'] += withTotalsDF[level1, level2]

        withTotalsDF = withTotalsDF.groupby(['Date']).sum()
        return withTotalsDF

    def _addTSBtoDF(self,df):
        pass

    def loadAndCreateSimpleDataFrame(self):
        f = open('TrainingDiary.json', encoding="utf-8")
        data = json.load(f)
        days = data['days']
        days.sort(key=lambda x: x['iso8061DateString'])

        dataDict = {}
        for d in DF_INDEX:
            dataDict[d] = []
        for d in DF_COLUMNS:
            dataDict[d] = []

        for d in days:
            date = dateutil.parser.parse(d['iso8061DateString']).date()
            if 'workouts' in d:
                tempDict = {}
                for w in d['workouts']:
                    dataDict[DF_DATE].append(date)
                    dataDict[DF_ACTIVITY].append(w['activityString'])
                    dataDict[DF_ACTIVITY_TYPE].append(w['activityTypeString'])
                    dataDict[DF_EQUIPMENT].append(w['equipmentName'])
                    subKey = f"{w['activityString']}:{w['activityTypeString']};{w['equipmentName']}"
                    count = tempDict.get(subKey,0) + 1
                    tempDict[subKey] = count
                    dataDict[DF_WORKOUT].append(count)
                    for u in DF_COLUMNS:
                        dataDict[u].append(w[u])

        df = pd.DataFrame(dataDict)
        # set up index as a proper date from DF_DATE column
        df.set_index([pd.DatetimeIndex(df[DF_DATE]), DF_ACTIVITY, DF_ACTIVITY_TYPE, DF_EQUIPMENT, DF_WORKOUT], inplace=True)
        # remove old date column as now have a proper date based one.
        df.drop([DF_DATE],axis=1,inplace=True)

        return df

    def createBar(self):
        df = self.loadAndCreateSimpleDataFrame()
        yearCounts = df.groupby([lambda x: x[0].year,'Activity']).count()['km']
        index = pd.MultiIndex.from_product([range(2004,2019),['Swim','Bike','Run','Other','Gym','Walk']])
        yearCounts = yearCounts.reindex(index, fill_value=0)

        fig, ax = plt.subplots(3,5, sharex=True, sharey=True)

        fig_size = plt.rcParams['figure.figsize']
        fig_size[0] = 50
        fig_size[1] = 50

        for y in range(2004, 2019):
            i = y - 2004
            row = (i // 5)
            col = i % 5
            ax[row, col].bar(yearCounts[y].index.values, yearCounts[y].values, color='b')
            ax[row, col].set_title(f' {y}', fontdict={'fontsize': 11}, loc='left', pad=-12)
            for x, v in enumerate(yearCounts[y].values):
                ax[row,col].text(v,x, f' {v}', color='blue', va='center')
        plt.subplots_adjust(wspace=0, hspace=0)

        plt.show()

    def createSingleBar(self):
        df = self.loadAndCreateSimpleDataFrame()
        yearCounts = df.groupby(['Activity']).count()['km']

        fig, ax = plt.figure(), plt.axes()

        ax.bar(yearCounts.index.values, yearCounts.values, color='b')
        for x, v in enumerate(yearCounts.values):
            ax.text(v,x, f' {v}', color='blue', va='center')

        plt.show()

    def monthlyKM(self):

        df = self.loadAndCreateSimpleDataFrame()
        monthKM = df.groupby(['Activity', lambda x: x[0].year, lambda x: x[0].month]).sum()['km']
        activities = monthKM.index.levels[0].values
        index = pd.MultiIndex.from_product([activities, range(2004,2019), range(1,13)])
        monthKM = monthKM.reindex(index, fill_value=0)

        newIndex = []
        for y in range(2004, 2019):
            for m in range(1, 13):
                newIndex.append(f'{calendar.month_abbr[m]}-{y}')

        monthKM.index = pd.MultiIndex.from_product([activities, newIndex])

        #activities to add
        add = [a for a in activities if monthKM[a].sum() > 0]
        print(add)

        plt.xkcd(randomness=1)
        fig, axes = plt.subplots(nrows=len(add), ncols=1, sharex=True)

        axis = 0
        for a in add:
            axes[axis].bar(monthKM[a].index, monthKM[a].values)
            axes[axis].set_title(f'{a} km', fontdict={'fontsize':8}, pad=-12)
            axis += 1

        for a in axes:
            for l in a.get_xticklabels():
                a.set_xticks(range(1,180,15))
                l.set_size(8)
            for l in a.get_yticklabels():
                l.set_size(8)
        plt.subplots_adjust(wspace=0, hspace=0)
        plt.show()

    def rYearsHoursStackedPlot(self):
        df = self.loadAndCreateTimeSeriesDataFrame()
        hoursDF = df['hours'].drop(['Total'], axis=1)
        # rolling sum can introduce tiny negative numbers
        np.around(hoursDF.rolling(365, min_periods=1).sum(), decimals=0).plot(kind='area', stacked=True)
        plt.show()

    def monthlyHoursArea(self):

        df = self.loadAndCreateSimpleDataFrame()

        # switch activity to column
        activityDF = df.unstack(level=1, fill_value=0)

        # insert hours column index
        for level2 in activityDF.columns.levels[1]:
            activityDF[DF_HOURS, level2] = activityDF[DF_SECONDS, level2] / 3600

        # add totals for each unit
        for level1 in activityDF.columns.levels[0]:
            activityDF[level1, DF_TOTAL] = 0
            for level2 in activityDF.columns.levels[1]:
                # check to avoid double counting total
                if level2 is not DF_TOTAL:
                    activityDF[level1, DF_TOTAL] += activityDF[level1, level2]

        monthlyActivityDF = activityDF.groupby([lambda x: x[0].year, lambda x: x[0].month]).sum()

        # monthKM = df.groupby(['Activity', lambda x: x[0].year, lambda x: x[0].month]).sum()['km']
        index = pd.MultiIndex.from_product([ range(2004,2019), range(1,13)])
        monthlyActivityDF = monthlyActivityDF.reindex(index, fill_value=0)

        newIndex = []
        for y in range(2004, 2019):
            for m in range(1, 13):
                newIndex.append(f'{calendar.month_abbr[m]}-{y}')

        monthlyActivityDF.index = index
        monthlyHoursDF = monthlyActivityDF[DF_HOURS].drop([DF_TOTAL],axis=1)

        monthlyHoursDF.plot(kind='area', stacked=True)
        plt.show()


    def annualHoursStack(self):

        df = self.loadAndCreateSimpleDataFrame()

        # switch activity to column
        activityDF = df.unstack(level=1, fill_value=0)

        # insert hours column index
        for level2 in activityDF.columns.levels[1]:
            activityDF[DF_HOURS, level2] = activityDF[DF_SECONDS, level2] / 3600

        # add totals for each unit
        for level1 in activityDF.columns.levels[0]:
            activityDF[level1, DF_TOTAL] = 0
            for level2 in activityDF.columns.levels[1]:
                # check to avoid double counting total
                if level2 is not DF_TOTAL:
                    activityDF[level1, DF_TOTAL] += activityDF[level1, level2]

        annualHoursDF = activityDF.groupby([lambda x: x[0].year]).sum()

        annualHoursDF = annualHoursDF[DF_HOURS].drop([DF_TOTAL],axis=1)

        annualHoursDF.plot(kind='bar', stacked=True, width=0.9)
        plt.show()

    def createWeightScatterOLD(self):
        weightDF = self.loadAndCreateWeightDF()
        weightDF = weightDF[(weightDF != 0).all(1)]

        x = weightDF['kg']
        y = weightDF['fatPercent']

        # definitions for the axes
        left, width = 0.1, 0.65
        bottom, height = 0.1, 0.65
        bottom_h = left_h = left + width + 0.02

        rect_scatter = [left, bottom, width, height]
        rect_histx = [left, bottom_h, width, 0.2]
        rect_histy = [left_h, bottom, 0.2, height]

        # start with a rectangular Figure
        plt.figure(1, figsize=(8, 8))
        # fig, ax = plt.subplots()

        axScatter = plt.axes(rect_scatter)
        axHistx = plt.axes(rect_histx)
        axHisty = plt.axes(rect_histy)

        # axScatter = ax(rect_scatter)
        # axHistx = ax(rect_histx)
        # axHisty = ax(rect_histy)

        # the scatter plot:
        axScatter.scatter(x, y)

        binwidth = 0.5
        xbins = np.arange(min(x), max(x) + binwidth, binwidth)
        ybins = np.arange(min(y), max(y) + binwidth, binwidth)

        axHistx.hist(x, bins=xbins)
        axHisty.hist(y, bins=ybins, orientation='horizontal')

        # axHistx.set_xlim(axScatter.get_xlim())
        # axHisty.set_ylim(axScatter.get_ylim())

        plt.show()

    def createWeightScatter(self):
        weightDF = self.loadAndCreateWeightDF()
        weightDF = weightDF[(weightDF != 0).all(1)]
        self.createScatter(weightDF['kg'],weightDF['fatPercent'],0.5)

    def createWeightHeatMap(self):
        weightDF = self.loadAndCreateWeightDF()
        weightDF = weightDF[(weightDF != 0).all(1)]
        self.createHeatMap(weightDF['kg'],weightDF['fatPercent'],20)

    def createScatter(self,x,y,binWidth):
        c, p1 = polyfit(x, y, 1)

        # start with a rectangular Figure
        fig = plt.figure()
        gs = gridspec.GridSpec(3, 3)

        axMain = fig.add_subplot(gs[1:, :2])
        ax1 = fig.add_subplot(gs[0, :2], sharex=axMain)
        ax2 = fig.add_subplot(gs[1:, 2], sharey=axMain)

        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_yticklabels(), visible=False)

        # the scatter plot:
        axMain.scatter(x, y)
        # add best fit
        axMain.plot(x, c + p1 * x, color='red', dashes=[3,3])

        xbins = np.arange(min(x), max(x) + binWidth, binWidth)
        ybins = np.arange(min(y), max(y) + binWidth, binWidth)

        ax1.hist(x, bins=xbins)
        ax2.hist(y, bins=ybins, orientation='horizontal')
        plt.subplots_adjust(wspace=0, hspace=0)

        plt.show()


    def createHeatMap(self,x,y,gridSize):

        plt.hexbin(x, y, gridsize=gridSize, cmap=cm.hot, bins=None)
        plt.axis([x.min(), x.max(), y.min(), y.max()])
        plt.grid(True, linestyle='-', alpha=0.5)

        cb = plt.colorbar()
        cb.set_label('observations')
        plt.show()

    def createTSBBar(self):

        timeSeriesDF = self.loadAndCreateTimeSeriesDataFrame()
        # get the activites as we'll be adding more columns and don't want them iterating over as that would prove inifinite !
        activities = timeSeriesDF.columns.levels[1]

        cDecay = np.exp(-1 / 42)
        cImpact = 1 - cDecay
        aDecay = np.exp(-1 / 7)
        aImpact = 1 - aDecay

        for a in activities:
            prevATL = prevCTL = 0
            atlArray = []
            ctlArray = []
            tsbArray = []
            for idx, tss in timeSeriesDF['tss'][a].items():
                ctl = tss * cImpact + prevCTL * cDecay
                atl = tss * aImpact + prevATL * aDecay
                atlArray.append(atl)
                ctlArray.append(ctl)
                tsbArray.append(ctl - atl)
                prevCTL = ctl
                prevATL = atl
            timeSeriesDF['tss', f'{a} CTL'] = ctlArray
            timeSeriesDF['tss', f'{a} ATL'] = atlArray
            timeSeriesDF['tss', f'{a} TSB'] = tsbArray

        start = '1/1/18'
        end = '31/12/18'
        displayTimeSeries = timeSeriesDF[start:end]
        days = len(displayTimeSeries)
        numberOfLabels = 4
        gap = days // numberOfLabels
        bins = range(gap // 2, days + 1 - (gap // 2), gap)
        for b in bins:
            print(b)
        fig, axes = plt.subplots(2, 2, sharex=True, sharey=True)
        # yax2 = axes[0, 0].twinx()
        axes[0, 0].plot(displayTimeSeries['tss'][['Swim CTL', 'Swim ATL', 'Swim TSB']])
        axes[0, 0].fill(displayTimeSeries['tss'].index.values, displayTimeSeries['tss']['Swim TSB'], 'b', alpha=0.3)
        axes[0, 0].bar(displayTimeSeries['tss'].index.values, displayTimeSeries['tss']['Swim'], color='red')
        axes[0, 0].set_title('Swim TSB', pad=-10)
        axes[1, 0].plot(displayTimeSeries['tss'][['Bike CTL', 'Bike ATL', 'Bike TSB']])
        axes[1, 0].fill(displayTimeSeries['tss'].index.values, displayTimeSeries['tss']['Bike TSB'], 'b', alpha=0.3)
        axes[1, 0].bar(displayTimeSeries['tss'].index.values, displayTimeSeries['tss']['Bike'], color='red')
        axes[1, 0].set_title('Bike TSB', pad=-10)

        axes[0, 1].plot(displayTimeSeries['tss'][['Run CTL', 'Run ATL', 'Run TSB']])
        axes[0, 1].fill(displayTimeSeries['tss'].index.values, displayTimeSeries['tss']['Run TSB'], 'b', alpha=0.3)
        axes[0, 1].bar(displayTimeSeries['tss'].index.values, displayTimeSeries['tss']['Run'], color='red')
        axes[0, 1].set_title('Run TSB', pad=-10)
        axes[1, 1].plot(displayTimeSeries['tss'][['Total CTL', 'Total ATL', 'Total TSB']])
        axes[1, 1].fill(displayTimeSeries['tss'].index.values, displayTimeSeries['tss']['Total TSB'], 'b', alpha=0.3)
        axes[1, 1].bar(displayTimeSeries['tss'].index.values, displayTimeSeries['tss']['Total'], color='red')
        axes[1, 1].set_title('Total TSB', pad=-10)

        fig.tight_layout()

        plt.subplots_adjust(wspace=0, hspace=0)
        axes[1, 0].xaxis.set_major_locator(mdates.MonthLocator())

        plt.subplots_adjust(wspace=0, hspace=0)
        plt.show()

    def setUpGui(self):
        testB = tk.Button(self.__root, text='Test', command=self.monthlyKM)
        multiB = tk.Button(self.__root, text='Multi Bars', command=self.createBar)
        singleB = tk.Button(self.__root, text='Bar', command=self.createSingleBar)
        stackB = tk.Button(self.__root, text='Monthly Hrs', command=self.monthlyHoursArea)
        annualHrsB = tk.Button(self.__root, text='Annual Hr', command=self.annualHoursStack)
        weightScatterB = tk.Button(self.__root, text='KG v %', command=self.createWeightScatter)
        kgHeatMapB = tk.Button(self.__root, text='KG Heatmap', command=self.createWeightHeatMap)
        tsbB = tk.Button(self.__root, text='TSB', command=self.createTSBBar)
        rYearHrsB = tk.Button(self.__root, text='rYear Hours', command=self.rYearsHoursStackedPlot)
        testB.grid(row=0,column=0, sticky='nsew')
        multiB.grid(row=0,column=1, sticky='nsew')
        singleB.grid(row=0,column=2, sticky='nsew')
        stackB.grid(row=0,column=3, sticky='nsew')
        annualHrsB.grid(row=0,column=4, sticky='nsew')
        weightScatterB.grid(row=0,column=5, sticky='nsew')
        tsbB.grid(row=0,column=6, sticky='nsew')
        kgHeatMapB.grid(row=0,column=7, sticky='nsew')
        rYearHrsB.grid(row=0,column=8, sticky='nsew')

        loadFileB = tk.Button(self.__root, text='Open Training Diary', command=self.openDiary)
        loadFileB.grid(row=1,column=0,sticky='nsew')

    def openDiary(self):
        fileName = filedialog.askopenfilename(initialdir='/~', title='Select file', filetypes=[('JSON','*.json')])
        print(fileName)

def main():
    root = tk.Tk()
    test = PlotTest(root)
    test.setUpGui()
    root.mainloop()

if __name__ == '__main__':
    main()