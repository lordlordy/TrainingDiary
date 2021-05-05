from abc import ABC, abstractmethod

from workoutentry.modelling.modelling_types import Aggregation


class AbstractRoller(ABC):

    @abstractmethod
    def roll_it_up(self,df):
        pass

    def title_component(self):
        return None


class NoOpRoller(AbstractRoller):

    def roll_it_up(self,df):
        return df

    def number_of_periods(self) -> int:
        return 1


class RollingDefinition(AbstractRoller):

    def __init__(self, periods, aggregation=Aggregation.SUM, incl_zeros=True):
        self.periods = periods
        self.aggregation = aggregation
        self.incl_zeroes = incl_zeros

    def title_component(self):
        return f"Rolling {self.periods}x"

    def number_of_periods(self) -> int:
        return self.periods

    def roll_it_up(self, df):
        if self.aggregation == Aggregation.SUM:
            return df.rolling(self.periods, min_periods=1).sum()
        elif self.aggregation == Aggregation.MEAN:
            return df.rolling(self.periods, min_periods=1).mean()
        elif self.aggregation == Aggregation.MAX:
            return df.rolling(self.periods, min_periods=1).max()
        elif self.aggregation == Aggregation.MEDIAN:
            return df.rolling(self.periods, min_periods=1).median()
        elif self.aggregation == Aggregation.MIN:
            return df.rolling(self.periods, min_periods=1).min()
        elif self.aggregation == Aggregation.STD_DEV:
            return df.rolling(self.periods, min_periods=1).std()
        return df