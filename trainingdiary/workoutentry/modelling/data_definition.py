import pandas as pd

from workoutentry.modelling.converters import measure_converter
from workoutentry.modelling.modelling_types import DayAggregation
from workoutentry.modelling.period import Period
from workoutentry.modelling.rolling import NoOpRoller
from workoutentry.training_data import TrainingDataManager
from workoutentry.training_data.utitilties import sql_for_aggregator


class DataDefinition:

    def __init__(self, activity='All', activity_type='All', equipment='All', measure='km', day_aggregation_method=DayAggregation.SUM, day_of_week='All', month='All', day_type='All'):
        self.activity = activity
        self.activity_type = activity_type
        self.equipment = equipment
        self.measure = measure
        self.day_aggregation_method = day_aggregation_method
        self.day_of_week = day_of_week
        self.month = month
        self.day_type = day_type
        self.converter = measure_converter(measure)
        self.target_measure = measure if self.converter is None else self.converter.underlying_measure()
        self.tdm = TrainingDataManager()

    def title_component(self):
        components = [self.activity]
        if self.activity_type != "All":
            components.append(self.activity_type)
        if self.equipment != "All":
            components.append(self.equipment)
        components.append(self.measure)
        return " ".join(components)

    def sql(self, time_period) -> str:
        tdm = TrainingDataManager();
        table = tdm.table_for_measure(self.measure)
        # SELECT
        sql = self.select_clause(table)
        sql += f" FROM {table} "
        # INNER JOIN TO DATE
        sql += self.inner_join(table)
        sql += f"WHERE "
        if table == 'Reading':
            sql += f"type='{self.measure}' AND "
        else:
            sql += self.where_clause()
        sql += f"Workout.date BETWEEN '{time_period.start}' and '{time_period.end}' GROUP BY Workout.date"
        return sql

    def inner_join(self, table) -> str:
        if self.day_type == "All":
            return ""
        return f"INNER JOIN Day On {table}.date = Day.date "

    def select_clause(self, table) -> str:
        if table == 'Reading':
            return f"SELECT Workout.date, {sql_for_aggregator(self.day_aggregation_method, 'value')} as {self.target_measure}"
        else:
            return f"SELECT Workout.date, {sql_for_aggregator(self.day_aggregation_method, self.target_measure)} as {self.target_measure}"

    def where_clause(self) -> str:
        wheres = list()
        sql = ""
        if self.activity != 'All':
            wheres.append(f"Workout.activity='{self.activity}'")
        if self.activity_type != 'All':
            wheres.append(f"Workout.activity_type='{self.activity_type}'")
        if self.equipment != 'All':
            wheres.append(f"Workout.equipment='{self.equipment}'")
        if self.day_type != 'All':
            wheres.append(f"Day.type='{self.day_type}'")
        if len(wheres) > 0:
            sql = f"{' AND '.join(wheres)} AND "
        return sql

    def day_data(self, time_period):
        df = self.tdm.day_data_df(time_period, self)
        if len(df) == 0:
            return None
        if self.converter is not None:
            df[self.measure] = df[self.target_measure].astype('float')
            df = df.drop(columns=[self.target_measure])
            df[self.measure] = df[self.measure].apply(self.converter.convert_lambda())
        df = df.set_index('date')
        df.index = pd.to_datetime(df.index)
        df = self.__fill_gaps(df)
        return df

    # todo currently just fills with zeroes - need to add not filling and interpolation methods
    def __fill_gaps(self, df):
        max_date = df.index.max()
        min_date = df.index.min()
        index = pd.date_range(min_date, max_date)
        df = df.reindex(index, fill_value=0)
        return df


class SeriesDefinition:
    NOT_SET = 'notSet'
    # todo - should measure and underlying_measure reference DataDefinition rather than just the name of the measure.
    # At the moment there's the chance that this measure in the SeriesDefinition does not match the measure it's been used on even though this does not make sense
    # This issue is the DataDefinition is not correct for definition things like CTL.
    def __init__(self, period=Period(), rolling_definition=NoOpRoller(), measure=NOT_SET, underlying_measure=NOT_SET):
        self.period = period
        self.rolling_definition = rolling_definition
        self.measure = measure
        self.underlying_measure = underlying_measure

    def title_component(self):
        title = self.period.title_component()
        rolling = self.rolling_definition.title_component()
        if rolling is not None:
            title += f" {rolling}"
        return title

    def set_measure(self, measure):
        self.measure = measure

    def is_rolling(self):
        return not isinstance(self.rolling_definition, NoOpRoller)