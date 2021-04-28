from workoutentry.modelling.data_definition import SeriesDefinition
from workoutentry.modelling.graph_defaults import Scales, TimeSeriesDefaults
from workoutentry.modelling.processor import NoOpProcessor


class TimeSeriesManager:

    class TimeSeriesSet:

        def __init__(self, data_definition, series_definition=SeriesDefinition(), processor=NoOpProcessor()):
            self.data_definition = data_definition
            self.series_definition = series_definition
            self.processor = processor

    def time_series(self, requested_time_period, time_series_list):
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

            time_series = self.__time_series(requested_time_period, tss, scales)

            if time_series is not None:
                ts_list += time_series
        title = ' / '.join(data_titles)
        if len(processor_titles) > 0:
            title += f" {' / '.join(processor_titles)}"
        return {'title': title,
                'datasets': ts_list,
                'scales': scales.data_dictionary()}

    def __time_series(self, requested_time_period, time_series_set, scales):

        time_period = time_series_set.processor.adjusted_time_period(requested_time_period)

        df = time_series_set.data_definition.day_data(time_period)
        if df is None:
            return None
        df = time_series_set.series_definition.period.aggregate_to_period(df)
        df = time_series_set.series_definition.rolling_definition.roll_it_up(df)
        df = time_series_set.processor.process(df)
        df.index = df.index.date

        if requested_time_period is not None:
            # filter back to original requested period
            df = df.loc[requested_time_period.start : requested_time_period.end]

        values_dict = {col: list() for col in df.columns.values if col != 'date'}

        for index, row in df.iterrows():
            for col in df.columns.values:
                if col != 'date':
                    values_dict[col].append({'x': index, 'y': float(row[col])})

        time_series = self.__add_graph_defaults(values_dict,
                                                time_series_set.processor.series_definitions(time_series_set.data_definition.measure, time_series_set.series_definition),
                                                scales)

        return time_series

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
