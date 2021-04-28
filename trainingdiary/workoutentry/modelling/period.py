from workoutentry.modelling.modelling_types import Aggregation, PandasPeriod
import pandas as pd


class Period:

    def __init__(self, label=PandasPeriod.DAY, aggregation=Aggregation.SUM, to_date=False):
        self.label = label
        self.aggregation = aggregation
        self.to_date = to_date

    def title_component(self):
        if self.label == 'Day':
            return 'Day'
        title = f"{self.label.value} {self.aggregation.value}"
        if self.to_date:
            title += " to date"
        return title

    def aggregate_to_period(self, df):
        if self.label != PandasPeriod.DAY:
            if self.aggregation == Aggregation.SUM:
                if self.to_date:
                    df = df.groupby(pd.Grouper(freq=self.label.value)).expanding().sum()
                else:
                    df = df.groupby(pd.Grouper(freq=self.label)).sum()
            elif self.aggregation == Aggregation.MEAN:
                if self.to_date:
                    df = df.groupby(pd.Grouper(freq=self.label)).expanding().mean()
                else:
                    df = df.groupby(pd.Grouper(freq=self.label)).mean()
            elif self.aggregation == Aggregation.MAX:
                if self.to_date:
                    df = df.groupby(pd.Grouper(freq=self.label)).expanding().max()
                else:
                    df = df.groupby(pd.Grouper(freq=self.label)).max()
            elif self.aggregation == Aggregation.MEDIAN:
                if self.to_date:
                    df = df.groupby(pd.Grouper(freq=self.label)).expanding().median()
                else:
                    df = df.groupby(pd.Grouper(freq=self.label)).median()
            elif self.aggregation == Aggregation.MIN:
                if self.to_date:
                    df = df.groupby(pd.Grouper(freq=self.label)).expanding().min()
                else:
                    df = df.groupby(pd.Grouper(freq=self.label)).min()
            elif self.aggregation == Aggregation.STD_DEV:
                if self.to_date:
                    df = df.groupby(pd.Grouper(freq=self.label)).expanding().std()
                else:
                    df = df.groupby(pd.Grouper(freq=self.label)).std()
            if self.to_date:
                df = df.reset_index(level=0, drop=True)
        return df