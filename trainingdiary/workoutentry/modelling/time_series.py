import numpy as np
import pandas as pd

from workoutentry.modelling.data_definition import SeriesDefinition
from workoutentry.graphs.graph_defaults import Scales, TimeSeriesDefaults
from workoutentry.modelling.processor import NoOpProcessor
from workoutentry.modelling.time_period import TimePeriod


class NoTimeSeriesDataException(Exception):

    def __init__(self, msg):
        self.msg = msg


class TimeSeriesManager:

    class TimeSeriesSet:

        def __init__(self, data_definition, series_definition=SeriesDefinition(), processor=NoOpProcessor(), x_axis_number=1):
            self.data_definition = data_definition
            self.series_definition = series_definition
            self.processor = processor
            self.x_axis_number = x_axis_number

        def adjusted_time_period(self, time_period) -> TimePeriod:
            processor_adjusted = self.processor.adjusted_time_period(time_period)
            series_adjusted = self.series_definition.adjusted_time_period(time_period)
            return TimePeriod(min(processor_adjusted.start, series_adjusted.start), time_period.end)

    def time_series_list(self, requested_time_period, time_series_list):
        ts_dict, errors = self._time_series_dict(requested_time_period, time_series_list)
        names = []
        date_dicts = []
        dates = set()
        for name, dd in ts_dict.items():
            names.append(name)
            date_dicts.append(dd)
            [dates.add(d) for d in dd.keys()]
        tsl = list()
        if len(date_dicts) > 0:
            for key in dates:
                row = {'date': key}
                for i in range(len(names)):
                    row[names[i]] = date_dicts[i].get(key, 0)
                tsl.append(row)
        return tsl, errors

    def _time_series_dict(self, requested_time_period, time_series_list):
        ts_list = {}
        errors = list()
        for time_series_set in time_series_list:
            try:
                title = time_series_set.data_definition.title_component()
                for name, values in self.__time_series_dict(requested_time_period, time_series_set).items():
                    ts_list[title] = values
            except NoTimeSeriesDataException as e:
                errors.append(e.msg)
        return ts_list , errors

    def time_series_graph(self, requested_time_period, time_series_list) -> object:
        scales = Scales()
        ts_list = list()
        data_titles = list()
        processor_titles = list()
        errors = list()
        for tss in time_series_list:
            data_title = tss.data_definition.title_component()
            if data_title not in data_titles:
                data_titles.append(data_title)
            if not tss.processor.no_op():
                processor_title = tss.processor.title_component()
                if processor_title not in processor_titles:
                    processor_titles.append(processor_title)

            try:
                time_series = self.__time_series_graph(requested_time_period, tss, scales)
                ts_list += time_series
            except NoTimeSeriesDataException as e:
                errors.append(e.msg)

        title = ' / '.join(data_titles)
        if len(processor_titles) > 0:
            title += f" {' / '.join(processor_titles)}"

        return {'title': title,
                'datasets': ts_list,
                'scales': scales.data_dictionary()}

    def __time_series_dict(self, requested_time_period, time_series_set):
        df = self.__time_series_df(requested_time_period, time_series_set)
        values_dict = {col: dict() for col in df.columns.values if col != 'date'}
        for index, row in df.iterrows():
            for col in df.columns.values:
                if col != 'date':
                    if not np.isnan(row[col]):
                        values_dict[col][str(index)] = float(row[col])
                    else:
                        values_dict[col][str(index)] = 0.0
        return values_dict

    def __time_series_graph(self, requested_time_period, time_series_set, scales):

        df = self.__time_series_df(requested_time_period, time_series_set)

        values_dict = {col: list() for col in df.columns.values if col != 'date'}

        for index, row in df.iterrows():
            for col in df.columns.values:
                if col != 'date':
                    if not np.isnan(row[col]):
                        values_dict[col].append({'x': index, 'y': float(row[col])})

        time_series = self.__add_graph_defaults(values_dict,
                                                time_series_set.processor.series_definitions(time_series_set.data_definition.measure, time_series_set.series_definition),
                                                scales,
                                                x_axis_number=time_series_set.x_axis_number)

        return time_series

    def __time_series_df(self, requested_time_period, time_series_set):
        time_period = time_series_set.adjusted_time_period(requested_time_period)

        df = time_series_set.data_definition.day_data(time_period)

        if df is None:
            raise NoTimeSeriesDataException('No data for time series')

        if time_series_set.series_definition.period.incl_zeroes:
            new_index = pd.date_range(start=time_period.start, end=time_period.end)
            df = df.reindex(new_index, fill_value=0.0)

        df = time_series_set.series_definition.period.aggregate_to_period(df)
        df = time_series_set.series_definition.rolling_definition.roll_it_up(df)
        df = time_series_set.processor.process(df)
        df.index = df.index.date

        if requested_time_period is not None:
            # filter back to original requested period
            df = df.loc[requested_time_period.start : requested_time_period.end]

        return df

    def __add_graph_defaults(self, values_dict, series_definitions, scales, x_axis_number=1) -> list:
        time_series = list()
        tsd = TimeSeriesDefaults()
        for measure, data in values_dict.items():
            defaults = tsd.defaults(series_definitions.get(measure, None))
            x_axis_id, y_axis_id = scales.add(defaults, x_axis_number)
            defaults.dataset.set_data(data)
            defaults.dataset.set_xaxis_id(x_axis_id)
            defaults.dataset.set_yaxis_id(y_axis_id)

            ds_dd = defaults.dataset.data_dictionary()
            ds_dd['DT_RowId'] = f"{ds_dd['DT_RowId']}-{x_axis_number}"
            time_series.append(ds_dd)
        return time_series
