import math
from abc import ABC, abstractmethod
from datetime import timedelta

import pandas as pd
import numpy as np

from workoutentry.modelling.time_period import TimePeriod
from workoutentry.modelling.data_definition import SeriesDefinition


class AbstractProcessor(ABC):

    @abstractmethod
    def process(self, df):
        pass

    @abstractmethod
    def no_op(self):
        pass

    def adjusted_time_period(self, tp) -> TimePeriod:
        return tp

    def series_definitions(self, base_measure, base_series_definition):
        base_series_definition.set_measure(base_measure)
        return {base_measure: base_series_definition}

    def title_component(self):
        return None


class NoOpProcessor(AbstractProcessor):

    def process(self, df):
        return df

    def no_op(self):
        return True


class TSBProcessor(AbstractProcessor):
    TARGET_PERCENTAGE = 0.05

    def __init__(self, atl_impact_days, atl_decay_days, ctl_impact_days, ctl_decay_days):
        self.ctl_decay = np.exp(-1 / ctl_decay_days)
        self.ctl_impact = 1 - np.exp(-1 / ctl_impact_days)
        self.atl_decay = np.exp(-1 / atl_decay_days)
        self.atl_impact = 1 - np.exp(-1 / atl_impact_days)
        self.pre_days = int(math.log(TSBProcessor.TARGET_PERCENTAGE) / math.log(self.ctl_decay))

    def no_op(self):
        return False

    def title_component(self):
        return 'Training Stress Balance'

    def adjusted_time_period(self, tp) -> TimePeriod:
        return TimePeriod(tp.start - timedelta(self.pre_days), tp.end)

    def series_definitions(self, base_measure, base_series_definition):
        dd = super().series_definitions(base_measure, base_series_definition)
        dd['atl'] = SeriesDefinition(measure='atl', underlying_measure=base_measure)
        dd['ctl'] = SeriesDefinition(measure='ctl', underlying_measure=base_measure)
        dd['tsb'] = SeriesDefinition(measure='tsb', underlying_measure=base_measure)
        return dd

    def process(self, df):
        df['date'] = df.index
        df['date_shift'] = pd.to_datetime(df['date'].shift(1))
        df['days'] = (df['date'] - df['date_shift']) / np.timedelta64(1, 'D')
        df['atl_impact'] = df[df.columns[0]] * self.atl_impact
        df['ctl_impact'] = df[df.columns[0]] * self.ctl_impact
        df['atl'] = df['atl_impact']
        df['ctl'] = df['ctl_impact']

        for i in range(1, len(df)):
            df.iloc[i, df.columns.get_loc('atl')] = df.iloc[i]['atl_impact'] + df.iloc[i - 1]['atl'] * pow(self.atl_decay, df.iloc[i]['days'])
            df.iloc[i, df.columns.get_loc('ctl')] = df.iloc[i]['ctl_impact'] + df.iloc[i - 1]['ctl'] * pow(self.ctl_decay, df.iloc[i]['days'])

        df['tsb'] = df['ctl'] - df['atl']

        df = df.drop(columns=['date', 'date_shift', 'atl_impact', 'ctl_impact', 'days'])
        return df