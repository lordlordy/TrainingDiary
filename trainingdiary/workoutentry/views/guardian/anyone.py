from workoutentry.views.anyone_access.choice_lists import ChoiceListForType
from workoutentry.views.anyone_access.summary import BikeSummary, TrainingSummary, CannedGraph, ReadingSummary
from workoutentry.views.anyone_access.time_series import TimeSeriesAccess
from workoutentry.views.anyone_access.years import YearSummary

ANYONE_RESOURCE_MAP = {
    BikeSummary.URL: BikeSummary,
    TrainingSummary.URL: TrainingSummary,
    CannedGraph.URL: CannedGraph,
    ChoiceListForType.URL: ChoiceListForType,
    YearSummary.URL: YearSummary,
    TimeSeriesAccess.URL: TimeSeriesAccess,
    ReadingSummary.URL: ReadingSummary

}