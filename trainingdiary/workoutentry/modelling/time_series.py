from datetime import timedelta

from workoutentry.modelling.converters import measure_converter
from workoutentry.modelling.graph_defaults import Scales, TimeSeriesDefaults
from workoutentry.modelling.modelling_types import DayAggregator
from workoutentry.modelling.time_period import TimePeriod
from workoutentry.modelling.tsb import TSBProcessor
from workoutentry.training_data import TrainingDataManager
import pandas as pd
import numpy as np
import math


def pre_days_for_tsb(ctl_decay_days) -> int:
    target_percentage = 0.05
    decay_per_day = np.exp(-1 / ctl_decay_days)
    days = math.log(target_percentage) / math.log(decay_per_day)
    return int(days)


class TimeSeriesManager:

    def __init__(self):
        self.tdm = TrainingDataManager()

    def time_series(self, requested_time_period, period='Day', aggregation='Sum', activity='All', activity_type='All', equipment='All',
                    measure='km', day_aggregation_method=DayAggregator.SUM, to_date=False, rolling=False, rolling_periods=0, rolling_aggregation='Sum',
                    day_of_week='All', month='All', day_type='All', recorded_only=False):

        if requested_time_period is None:
            time_period = self.tdm.diary_time_period()
        else:
            time_period = self.__adjusted_time_period(42, requested_time_period)
        df = self.__day_data(time_period, activity, activity_type, equipment, measure, day_aggregation_method)
        df = self.__fill_gaps(df, 'zeros')
        tsb = TSBProcessor(7, 7, 42, 42)
        df = tsb.process(df)
        df.index = df.index.date

        if requested_time_period is not None:
            # filter back to original requested period
            df = df.loc[requested_time_period.start : requested_time_period.end]

        values_dict = {col: list() for col in df.columns.values if col != 'date'}

        for index, row in df.iterrows():
            for col in df.columns.values:
                if col != 'date':
                    values_dict[col].append({'x': index, 'y': float(row[col])})

        return self.__add_graph_defaults(values_dict)

    def __add_graph_defaults(self, values_dict) -> dict:
        scales = Scales()
        time_series = list()
        tsd = TimeSeriesDefaults()
        for measure, data in values_dict.items():
            defaults = tsd.defaults(measure)
            scale_id = scales.add(defaults)
            defaults.dataset.set_data(data)
            defaults.dataset.set_yaxis_id(scale_id)
            time_series.append(defaults.dataset.data_dictionary())
        return {'datasets': time_series,
                'scales': scales.data_dictionary()}

    def __day_data(self, time_period, activity, activity_type, equipment, measure, aggregation_method):
        converter = measure_converter(measure)
        target_measure = measure if converter is None else converter.underlying_measure()
        df = self.tdm.day_data_df(time_period, activity, activity_type, equipment, target_measure, aggregation_method)
        if converter is not None:
            df[measure] = df[target_measure].astype('float')
            df = df.drop(columns=[target_measure])
            df[measure] = df[measure].apply(converter.convert_lambda())
        df = df.set_index('date')
        df.index = pd.to_datetime(df.index)
        return df

    def __fill_gaps(self, df, interpolation_method):
        max_date = df.index.max()
        min_date = df.index.min()
        index = pd.date_range(min_date, max_date)
        df = df.reindex(index, fill_value=0)
        return df

    def __adjusted_time_period(self, ctl_decay_days, tp):
        days = pre_days_for_tsb(42)
        print(days)
        return TimePeriod(tp.start - timedelta(days), tp.end)