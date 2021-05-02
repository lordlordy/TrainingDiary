from workoutentry.views.me.data_access import DataForDate, NextDiaryDate, SaveDay, ReadingsLeftForDay, SaveNewReadings, SaveWorkout, DeleteWorkout, DeleteReading
from workoutentry.views.anyone_access.choice_lists import ChoiceListForType

ME_RESOURCE_MAP = {
    DataForDate.URL: DataForDate,
    NextDiaryDate.URL: NextDiaryDate,
    SaveDay.URL: SaveDay,
    ReadingsLeftForDay.URL: ReadingsLeftForDay,
    SaveNewReadings.URL: SaveNewReadings,
    SaveWorkout.URL: SaveWorkout,
    DeleteWorkout.URL: DeleteWorkout,
    DeleteReading.URL: DeleteReading
}