from workoutentry.views.anyone_access.summary import BikeSummary, TrainingSummary, TSBData

ANYONE_RESOURCE_MAP = {
    BikeSummary.URL: BikeSummary,
    TrainingSummary.URL: TrainingSummary,
    TSBData.URL: TSBData
}