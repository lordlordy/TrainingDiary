from workoutentry.modelling.modelling_types import DayAggregation


def sql_for_aggregator(aggregator, measure) -> str:
    if aggregator == DayAggregation.SUM:
        return f"sum({measure})"
    elif aggregator == DayAggregation.MEAN:
        return f"avg({measure})"
    elif aggregator == DayAggregation.MAX:
        return f"max({measure})"
    elif aggregator == DayAggregation.MIN:
        return f"min({measure})"
    elif aggregator == DayAggregation.TIME_WEIGHTED_AVERAGE:
        return f"sum({measure} * seconds) / sum(seconds)"
    elif aggregator == DayAggregation.DISTANCE_WEIGHTED_AVERAGE:
        return f"sum({measure} * km) / sum(km)"

