import json
import pandas as pd
import numpy as np
import dateutil.parser
from functools import reduce
import operator
from datetime import date

import matplotlib
# this line needed to stop it crashing when using in tkinter
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter

DF_DATE, DF_ACTIVITY, DF_ACTIVITY_TYPE, DF_EQUIPMENT, DF_WORKOUT = 'Date', 'Activity', 'Activity Type', 'Equipment', 'Workout #'
DF_ASCENT_METRES, DF_KJ, DF_SECONDS, DF_REPS, DF_KM, DF_TSS, DF_BRICK, DF_RPE, DF_WATTS, DF_CADENCE, DF_HR = 'ascentMetres', 'kj', 'seconds', 'reps', 'km', 'tss', 'brick', 'rpe', 'watts', 'cadence', 'hr'

DF_INDEX = [DF_DATE, DF_ACTIVITY, DF_ACTIVITY_TYPE, DF_EQUIPMENT, DF_WORKOUT]
DF_COLUMNS = [DF_ASCENT_METRES, DF_KJ, DF_SECONDS, DF_REPS, DF_KM, DF_TSS, DF_BRICK, DF_RPE, DF_WATTS, DF_CADENCE, DF_HR]

class PlotTest:

    def __init__(self, root=None):
        self.__root = root
        self.setUpGui()

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
        df.set_index([pd.DatetimeIndex(df[DF_DATE]), DF_ACTIVITY, DF_ACTIVITY_TYPE, DF_EQUIPMENT, DF_WORKOUT], inplace=True)
        df.drop([DF_DATE],axis=1,inplace=True)

        return df

    def test(self):

        df = self.loadAndCreateSimpleDataFrame()
        monthTotals = df.groupby(['Activity', lambda x: x[0].year, lambda x: x[0].month]).sum()
        index = pd.MultiIndex.from_product([['Swim','Bike','Run','Other','Gym', 'Walk'], range(2004,2019), range(1,13)])
        monthTotals = monthTotals.reindex(index, fill_value=0)

        print(monthTotals)

        # df['Km Bucket'] = pd.cut(df['km'],[0,100,200,300,400])
        # pd.set_option('display.max_columns',12)
        # pd.set_option('display.max_rows', 500)

        plt.xkcd(randomness=1)
        fig, axes = plt.subplots(nrows=3, ncols=1)

        locs, labels = plt.xticks()
        print(locs)
        for l in labels:
            print(l)

        a = axes[0]

        axes[0].set_ylabel('KM')
        axes[1].set_ylabel('KM')
        axes[2].set_ylabel('KM')


        monthTotals['km'].loc['Swim'].plot(ax=axes[0], kind='bar', sharex=True, width=1)
        axes[0].set_title('Swim')
        monthTotals['km'].loc['Bike'].plot(ax=axes[1], kind='bar', sharex=True, width=1)
        axes[1].set_title('Bike')
        monthTotals['km'].loc['Run'].plot(ax=axes[2], kind='bar', width=1)
        axes[2].set_title('Run')

        axes[0].set_xticks([])
        axes[1].set_xticks([])
        plt.locator_params(axis='x', nbins=10)
        plt.locator_params(axis='y', nbins=5)



        canvas = FigureCanvasTkAgg(fig, master=self.__root)
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, self.__root)
        toolbar.update()
        canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # plt.show()

    def setUpGui(self):
        showButton = tkinter.Button(self.__root, text='Show', command=self.test)
        showButton.pack()

def main():
    root = tkinter.Tk()
    test = PlotTest(root)
    root.mainloop()

if __name__ == '__main__':
    main()