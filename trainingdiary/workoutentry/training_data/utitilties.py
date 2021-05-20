from workoutentry.modelling.modelling_types import DayAggregation


def sql_for_aggregator(aggregator, measure) -> str:
    if aggregator == DayAggregation.SUM or aggregator == DayAggregation.SUM.value:
        return f"sum({measure})"
    elif aggregator == DayAggregation.MEAN or aggregator == DayAggregation.MEAN.value:
        return f"avg({measure})"
    elif aggregator == DayAggregation.MAX or aggregator == DayAggregation.MAX.value:
        return f"max({measure})"
    elif aggregator == DayAggregation.MIN or aggregator == DayAggregation.MIN.value:
        return f"min({measure})"
    elif aggregator == DayAggregation.TIME_WEIGHTED_AVERAGE or aggregator == DayAggregation.TIME_WEIGHTED_AVERAGE.value:
        return f"sum({measure} * seconds) / sum(seconds)"
    elif aggregator == DayAggregation.DISTANCE_WEIGHTED_AVERAGE or aggregator == DayAggregation.DISTANCE_WEIGHTED_AVERAGE.value:
        return f"sum({measure} * km) / sum(km)"

