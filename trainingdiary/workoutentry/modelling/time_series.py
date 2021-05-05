import numpy as np
import pandas as pd

from workoutentry.modelling.data_definition import SeriesDefinition
from workoutentry.modelling.graph_defaults import Scales, TimeSeriesDefaults
from workoutentry.modelling.processor import NoOpProcessor


class TimeSeriesManager:

    class TimeSeriesSet:

        def __init__(self, data_definition, series_definition=SeriesDefinition(), processor=NoOpProcessor()):
            self.data_definition = data_definition
            self.series_definition = series_definition
            self.processor = processor

    def time_series_list(self, requested_time_period, time_series_list):
        ts_dict = self.time_series_dict(requested_time_period, time_series_list)
        names = []
        date_dicts = []
        for name, dd in ts_dict.items():
            names.append(name)
            date_dicts.append(dd)
        tsl = list()
        if len(date_dicts) > 0:
            for key in date_dicts[0].keys():
                row = {'date': key}
                for i in range(len(names)):
                    row[names[i]] = date_dicts[i][key]
                tsl.append(row)
        return tsl

    def time_series_dict(self, requested_time_period, time_series_list):
        ts_list = {}
        for time_series_set in time_series_list:
            title = time_series_set.data_definition.title_component()
            for name, values in self.__time_series_dict(requested_time_period, time_series_set).items():
                ts_list[title] = values
        return ts_list

    def time_series_graph(self, requested_time_period, time_series_list) -> object:
        scales = Scales()
        ts_list = list()
        data_titles = list()
        processor_titles = list()
        for tss in time_series_list:
            data_title = tss.data_definition.title_component()
            if data_title not in data_titles:
                data_titles.append(data_title)
            if not tss.processor.no_op():
                processor_title = tss.processor.title_component()
                if processor_title not in processor_titles:
                    processor_titles.append(processor_title)

            time_series = self.__time_series_graph(requested_time_period, tss, scales)

            if time_series is not None:
                ts_list += time_series

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
                                                scales)

        return time_series

    def __time_series_df(self, requested_time_period, time_series_set):
        time_period = time_series_set.processor.adjusted_time_period(requested_time_period)

        df = time_series_set.data_definition.day_data(time_period)

        if df is None:
            return None

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

    def __add_graph_defaults(self, values_dict, series_definitions, scales) -> list:
        time_series = list()
        tsd = TimeSeriesDefaults()
        for measure, data in values_dict.items():
            defaults = tsd.defaults(series_definitions.get(measure, None))
            scale_id = scales.add(defaults)
            defaults.dataset.set_data(data)
            defaults.dataset.set_yaxis_id(scale_id)
            time_series.append(defaults.dataset.data_dictionary())
        return time_series
