import pandas as pd

class Graph:

    TYPE = 'graph_type'
    AXIS = 'axis'
    SIZE = 'size'
    PLOT_ZEROES = 'plot_zeroes'
    GRAPH_VARIABLES = [TYPE, AXIS, SIZE, PLOT_ZEROES]

    T_LINE = 'Line'
    T_FILL = 'Fill'
    T_BAR = 'Bar'
    T_POINT = 'Point'
    T_SCATTER = 'Scatter'
    T_SCATTER_HISTOGRAM = 'Scatter-Hist'
    T_HEATMAP = 'Heatmap'
    T_HISTOGRAM = 'Histogram'

    AXIS_PRIMARY = 'Primary'
    AXIS_SECONDARY = 'Secondary'

    SHARE_NONE = 'None'
    SHARE_BOTH = 'Both'
    SHARE_X = 'X Axis'
    SHARE_Y = 'Y Axis'

    GRAPH_TYPES = [T_LINE, T_FILL, T_POINT, T_BAR, T_SCATTER, T_SCATTER_HISTOGRAM, T_HEATMAP, T_HISTOGRAM]
    GRAPH_AXES = [AXIS_PRIMARY, AXIS_SECONDARY]
    AXIS_SHARE_OPTIONS = [SHARE_NONE, SHARE_BOTH, SHARE_X, SHARE_Y]

    def __init__(self, name, time_series, **kwargs):

        self.name = name
        self.time_series = pd.Series([i[1] for i in time_series], [i[0] for i in time_series])

        # set up default graph spec
        self.__graph_dict = {Graph.TYPE: Graph.T_LINE,
                             Graph.AXIS: Graph.AXIS_PRIMARY,
                             Graph.SIZE: 3,
                             Graph.PLOT_ZEROES: True}

        # override defaults with any values passed in
        for k in kwargs:
            if k in self.__graph_dict:
                self.__graph_dict[k] = kwargs[k]


    def plot_zeroes(self):
        return self.__graph_dict[Graph.PLOT_ZEROES]

    def is_primary(self):
        return self.__graph_dict[Graph.AXIS] == Graph.AXIS_PRIMARY

    def is_secondary(self):
        return self.__graph_dict[Graph.AXIS] == Graph.AXIS_SECONDARY

    def is_point(self):
        return self.__graph_dict[Graph.TYPE] == Graph.T_POINT

    def is_fill(self):
        return self.__graph_dict[Graph.TYPE] == Graph.T_FILL

    def is_bar(self):
        return self.__graph_dict[Graph.TYPE] == Graph.T_BAR

    def is_histogram(self):
        return self.__graph_dict[Graph.TYPE] == Graph.T_HISTOGRAM

    def is_scatter(self):
        return (self.__graph_dict[Graph.TYPE] == Graph.T_SCATTER
                or self.__graph_dict[Graph.TYPE] == Graph.T_SCATTER_HISTOGRAM
                or self.__graph_dict[Graph.TYPE] == Graph.T_HEATMAP)

    def is_scatter_histogram(self):
        return self.__graph_dict[Graph.TYPE] == Graph.T_SCATTER_HISTOGRAM

    def is_heat(self):
        return self.__graph_dict[Graph.TYPE] == Graph.T_HEATMAP

    def size(self):
        return self.__graph_dict[Graph.SIZE]

    def marker_size(self):
        return self.__graph_dict[Graph.SIZE]

    def marker(self):
        if self.is_point():
            return '.'
        else:
            return 'None'

    def line_style(self):
        if self.is_point():
            return 'None'
        else:
            return '-'