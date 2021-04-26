from workoutentry.modelling.modelling_types import DayAggregator
from workoutentry.training_data import TrainingDataManager
import pandas as pd


class TimeSeriesManager:

    def time_series(self, time_period, period='Day', aggregation='Sum', activity='All', activity_type='All', equipment='All',
                    measure='km' , day_aggregation_method=DayAggregator.SUM, to_date=False, rolling=False, rolling_periods=0, rolling_aggregation='Sum',
                    day_of_week='All', month='All', day_type='All', recorded_only=False):

        df = self.__day_data(time_period, activity, activity_type, equipment, measure, day_aggregation_method)
        df = self.__fill_gaps(df, 'zeros')
        df.index = df.index.date

        values_dict = {col: list() for col in df.columns.values}

        for index, row in df.iterrows():
            for col in df.columns.values:
                values_dict[col].append({'x': index, 'y': float(row[col])})

        return values_dict

    def __day_data(self, time_period, activity, activity_type, equipment, measure, aggregation_method):
        tdm = TrainingDataManager()
        df = tdm.day_data_df(time_period, activity, activity_type, equipment, measure, aggregation_method)

        return df

    def __fill_gaps(self, df, method):
        max_date = df.index.max()
        min_date = df.index.min()
        index = pd.date_range(min_date, max_date)
        df = df.reindex(index, fill_value=0)
        return df
