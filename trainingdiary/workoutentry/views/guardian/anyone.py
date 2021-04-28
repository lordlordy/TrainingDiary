from workoutentry.views.anyone_access.summary import BikeSummary, TrainingSummary, CannedGraph

ANYONE_RESOURCE_MAP = {
    BikeSummary.URL: BikeSummary,
    TrainingSummary.URL: TrainingSummary,
    CannedGraph.URL: CannedGraph
}