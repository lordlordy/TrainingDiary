from workoutentry.modelling.modelling_types import Aggregation, PandasPeriod
import pandas as pd


class Period:

    @staticmethod
    def generate_unique_key(pandas_period, aggregation, to_date, incl_zeros) -> str:
        s = f"{pandas_period.value}-{aggregation.value}"
        if to_date:
            s += "-to_date"
        if not incl_zeros:
            s += "-excl_zeroes"
        return s

    def __init__(self, pandas_period=PandasPeriod.DAY, aggregation=Aggregation.SUM, to_date=False, incl_zeroes=True):
        self.pandas_period = pandas_period
        self.aggregation = aggregation
        self.to_date = to_date
        self.incl_zeroes = incl_zeroes

    def unique_key(self) -> str:
        return Period.generate_unique_key(self.pandas_period, self.aggregation, self.to_date, self.incl_zeroes)

    def title_component(self):
        if self.pandas_period == 'Day':
            return 'Day'
        title = f"{self.pandas_period.value} {self.aggregation.value}"
        if self.to_date:
            title += " to date"
        return title

    def period_length_estimate(self) -> int:
        if self.to_date:
            return 1
        else:
            return self.pandas_period.length_estimate()

    def aggregate_to_period(self, df):
        if self.pandas_period != PandasPeriod.DAY:
            if self.aggregation == Aggregation.SUM:
                if self.to_date:
                    df = df.groupby(pd.Grouper(freq=self.pandas_period.value)).expanding().sum()
                else:
                    df = df.groupby(pd.Grouper(freq=self.pandas_period.value)).sum()
            elif self.aggregation == Aggregation.MEAN:
                if self.to_date:
                    df = df.groupby(pd.Grouper(freq=self.pandas_period.value)).expanding().mean()
                else:
                    df = df.groupby(pd.Grouper(freq=self.pandas_period.value)).mean()
            elif self.aggregation == Aggregation.MAX:
                if self.to_date:
                    df = df.groupby(pd.Grouper(freq=self.pandas_period.value)).expanding().max()
                else:
                    df = df.groupby(pd.Grouper(freq=self.pandas_period.value)).max()
            elif self.aggregation == Aggregation.MEDIAN:
                if self.to_date:
                    df = df.groupby(pd.Grouper(freq=self.pandas_period.value)).expanding().median()
                else:
                    df = df.groupby(pd.Grouper(freq=self.pandas_period.value)).median()
            elif self.aggregation == Aggregation.MIN:
                if self.to_date:
                    df = df.groupby(pd.Grouper(freq=self.pandas_period.value)).expanding().min()
                else:
                    df = df.groupby(pd.Grouper(freq=self.pandas_period.value)).min()
            elif self.aggregation == Aggregation.STD_DEV:
                if self.to_date:
                    df = df.groupby(pd.Grouper(freq=self.pandas_period.value)).expanding().std()
                else:
                    df = df.groupby(pd.Grouper(freq=self.pandas_period.value)).std()
            if self.to_date:
                df = df.reset_index(level=0, drop=True)
        return df