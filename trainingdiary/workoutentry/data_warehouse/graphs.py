from .data_warehouse import DataWarehouse


class ScatterGraph:

    def __init__(self, x_graph, y_graph):
        self.x = x_graph
        self.y = y_graph


class Graph:

    TYPE = 'graph_type'
    AXIS = 'axis'
    SIZE = 'size'
    GRAPH_VARIABLES = [TYPE, AXIS, SIZE]

    T_LINE = 'Line'
    T_FILL = 'Fill'
    T_BAR = 'Bar'
    T_POINT = 'Point'
    T_SCATTER = 'Scatter'
    T_HEATMAP = 'Heatmap'

    AXIS_PRIMARY = 'Primary'
    AXIS_SECONDARY = 'Secondary'

    GRAPH_TYPES = [T_LINE, T_FILL, T_POINT, T_BAR, T_SCATTER, T_HEATMAP]
    GRAPH_AXES = [AXIS_PRIMARY, AXIS_SECONDARY]

    def __init__(self, **kwargs):

        self.__ts_dict = {DataWarehouse.PERIOD: 'Day',
                          DataWarehouse.AGGREGATION: 'Sum',
                          DataWarehouse.ACTIVITY: 'All',
                          DataWarehouse.ACTIVITY_TYPE: 'All',
                          DataWarehouse.EQUIPMENT: 'All',
                          DataWarehouse.MEASURE: 'km',
                          DataWarehouse.TO_DATE: False,
                          DataWarehouse.ROLLING: False,
                          DataWarehouse.ROLLING_PERIODS: 0,
                          DataWarehouse.ROLLING_AGGREGATION: 'Sum',
                          DataWarehouse.DAY_OF_WEEK: 'All',
                          DataWarehouse.MONTH: 'All',
                          DataWarehouse.DAY_TYPE: 'All'}

        self.__graph_dict = {Graph.TYPE: Graph.T_LINE,
                             Graph.AXIS: Graph.AXIS_PRIMARY,
                             Graph.SIZE: 3}

        for k in kwargs:
            if k in self.__ts_dict:
                self.__ts_dict[k] = kwargs[k]
            elif k in self.__graph_dict:
                self.__graph_dict[k] = kwargs[k]

    def __str__(self):
        return f'{self.__ts_dict[DataWarehouse.PERIOD]}:{self.__ts_dict[DataWarehouse.ACTIVITY]}:{self.__ts_dict[DataWarehouse.MEASURE]}'

    def time_series(self):
        return DataWarehouse.instance().time_series(**self.__ts_dict)

    def is_primary(self):
        return self.__graph_dict[Graph.AXIS] == Graph.AXIS_PRIMARY

    def is_secondary(self):
        return self.__graph_dict[Graph.AXIS] == Graph.AXIS_SECONDARY

    def is_point(self):
        return self.__graph_dict[Graph.TYPE] == Graph.T_POINT

    def is_bar(self):
        return self.__graph_dict[Graph.TYPE] == Graph.T_BAR

    def is_scatter(self):
        return self.__graph_dict[Graph.TYPE] == Graph.T_SCATTER

    def size(self):
        return self.__graph_dict[Graph.SIZE]

    def marker_size(self):
        return self.__graph_dict[Graph.SIZE]

    def is_rolling(self):
        return self.__ts_dict[DataWarehouse.ROLLING] and self.__ts_dict[DataWarehouse.ROLLING_PERIODS] > 0

    def is_day_not_rolling(self):
        return self.__ts_dict[DataWarehouse.PERIOD] == 'Day' and not self.is_rolling()

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