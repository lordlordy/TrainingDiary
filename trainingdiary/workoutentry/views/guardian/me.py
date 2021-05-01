from workoutentry.views.me.data_access import DataForDate, ChoiceListForType, NextDiaryDate, SaveDay, ReadingsLeftForDay, SaveNewReadings, SaveWorkout, DeleteWorkout, DeleteReading

ME_RESOURCE_MAP = {
    DataForDate.URL: DataForDate,
    ChoiceListForType.URL: ChoiceListForType,
    NextDiaryDate.URL: NextDiaryDate,
    SaveDay.URL: SaveDay,
    ReadingsLeftForDay.URL: ReadingsLeftForDay,
    SaveNewReadings.URL: SaveNewReadings,
    SaveWorkout.URL: SaveWorkout,
    DeleteWorkout.URL: DeleteWorkout,
    DeleteReading.URL: DeleteReading
}