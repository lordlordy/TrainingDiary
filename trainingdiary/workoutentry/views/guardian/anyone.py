from workoutentry.views.anyone_access.choice_lists import ChoiceListForType
from workoutentry.views.anyone_access.eddington import EddingtonNumberCalculation
from workoutentry.views.anyone_access.summary import BikeSummary, TrainingSummary, CannedGraph

ANYONE_RESOURCE_MAP = {
    BikeSummary.URL: BikeSummary,
    TrainingSummary.URL: TrainingSummary,
    CannedGraph.URL: CannedGraph,
    ChoiceListForType.URL: ChoiceListForType,
    EddingtonNumberCalculation.URL: EddingtonNumberCalculation

}