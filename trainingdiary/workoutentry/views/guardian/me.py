from workoutentry.views.login import TrainingDiaryLogout
from workoutentry.views.me.data_access import DataForDate, NextDiaryDate, SaveDay, ReadingsLeftForDay, SaveNewReadings, SaveWorkout, DeleteWorkout, DeleteReading
from workoutentry.views.me.graph_defaults import SaveGraphDefaults, GetGraphDefaults, DeleteGraphDefaults

ME_RESOURCE_MAP = {
    DataForDate.URL: DataForDate,
    NextDiaryDate.URL: NextDiaryDate,
    SaveDay.URL: SaveDay,
    ReadingsLeftForDay.URL: ReadingsLeftForDay,
    SaveNewReadings.URL: SaveNewReadings,
    SaveWorkout.URL: SaveWorkout,
    DeleteWorkout.URL: DeleteWorkout,
    DeleteReading.URL: DeleteReading,
    TrainingDiaryLogout.URL: TrainingDiaryLogout,
    SaveGraphDefaults.URL: SaveGraphDefaults,
    GetGraphDefaults.URL: GetGraphDefaults,
    DeleteGraphDefaults.URL: DeleteGraphDefaults
}