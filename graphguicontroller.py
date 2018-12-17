import urllib
import os
import trainingdiarydataframes as tddf
from graphgui import GraphGUI
import tkinter as tk
import pandas as pd
import numpy as np

TYPE_JSON = '.json'
TYPE_SQLITE = '.db'
G_LINE = 'Line'
G_BAR = 'Bar'
G_SCATTER = 'Scatter'
G_MIXED = 'Mixed'
GRAPH_TYPES = [G_BAR, G_LINE, G_MIXED, G_SCATTER]

class GraphGUIController:

    def __init__(self, gui):
        self.__tddf = gui
        self._gui = gui
        self.__series_dict = {}
        self._gui.set_controller(self)

    def set_training_diary_data_frame(self,from_url):
        p = urllib.parse.urlparse(from_url)
        type = os.path.splitext(p.path)[1]
        if type == TYPE_JSON:
            self.__tddf = tddf.TDDataFramesJSON(from_url)
        elif type == TYPE_SQLITE:
            self.__tddf = tddf.TDDataFramesSQLITE(from_url)
        else:
            return
        self._gui.diary_name_label.set(from_url)

        self._gui.set_option_menu_items(GraphGUI.UNIT, self.__tddf.get_units())
        self._gui.set_option_menu_items(GraphGUI.ACTIVITY, self.__tddf.get_activities())
        self._gui.set_option_menu_items(GraphGUI.PERIOD, self.__tddf.get_periods())
        self._gui.set_option_menu_items(GraphGUI.WORKOUT_AGGREGATOR, self.__tddf.get_workouts_aggregators())
        self._gui.set_option_menu_items(GraphGUI.PERIOD_AGGREGATOR, self.__tddf.get_period_aggregators())
        self._gui.set_option_menu_items(GraphGUI.ACTIVITY_TYPE, self.__tddf.get_activity_types())
        self._gui.set_option_menu_items(GraphGUI.EQUIPMENT, self.__tddf.get_equipment())
        self._gui.set_option_menu_items(GraphGUI.DAY_TYPE, self.__tddf.get_day_types())
        self._gui.set_option_menu_items(GraphGUI.SLEEP_QUALITY, self.__tddf.get_sleep_quality())
        self._gui.set_option_menu_items(GraphGUI.DAY, self.__tddf.get_days())
        self._gui.set_option_menu_items(GraphGUI.MONTH, self.__tddf.get_months())
        # self._gui.set_option_menu_items(GraphGUI.GRAPH, GRAPH_TYPES)

    def file_name(self):
        return self.__tddf.file_name

    def create_series(self, for_name, **kwargs):
        self.__series_dict[for_name] = self.__tddf.get_series(**kwargs).rename(for_name)
        return len(self.__series_dict[for_name])

    def get_series(self, for_name):
        if for_name in self.__series_dict:
            return self.__series_dict[for_name]

    def get_scatter_data(self, x_name, y_name):
        # this removes NAN and makes sure x & y same length
        x = self.get_series(x_name)
        y = self.get_series(y_name)
        x = x[np.isfinite(x)]
        y = y[np.isfinite(y)]
        if len(x) == len(y):
            return {'x': x.values, 'y': y.values}
        elif len(x) - len(y) == 1:
            x.drop(x.index[0],inplace=True)
            return {'x': x.values, 'y': y.values}
        elif len(y) - len(x) == 1:
            y.drop(y.index[0],inplace=True)
            return {'x': x.values, 'y': y.values}
        else:
            df = pd.concat([x, y], axis=1)
            df = df[(np.isfinite(df)).all(1)]
        return {'x': df[x_name], 'y': df[y_name]}

    def get_df_for_series(self, series_names):
        series = []
        for s in series_names:
            if s in self.__series_dict:
                series.append(self.__series_dict[s])
        df = pd.concat(series, axis=1)
        return df

def main():
    root = tk.Tk()
    GraphGUIController(GraphGUI(root))
    root.mainloop()


if __name__ == '__main__':
    main()