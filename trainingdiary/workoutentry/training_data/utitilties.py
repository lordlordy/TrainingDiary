from workoutentry.modelling.modelling_types import DayAggregator


def sql_for_aggregator(aggregator, measure) -> str:
    if aggregator == DayAggregator.SUM:
        return f"sum({measure})"
    elif aggregator == DayAggregator.MEAN:
        return f"avg({measure})"
    elif aggregator == DayAggregator.MAX:
        return f"max({measure})"
    elif aggregator == DayAggregator.MIN:
        return f"min({measure})"
    elif aggregator == DayAggregator.TIME_WEIGHTED_AVERAGE:
        return f"sum({measure} * seconds) / sum(seconds)"
    elif aggregator == DayAggregator.DISTANCE_WEIGHTED_AVERAGE:
        return f"sum({measure} * km) / sum(km)"

