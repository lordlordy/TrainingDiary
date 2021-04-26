from enum import Enum


class DayAggregator(Enum):
    SUM = "Sum"
    MEAN = "Mean"
    MAX = "Max"
    MIN = "Min"
    TIME_WEIGHTED_AVERAGE = "Time Weighted Average"
    DISTANCE_WEIGHTED_AVERAGE = "Distance Weight Average"



