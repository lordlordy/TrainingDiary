from workoutentry.views.me.data_access import DataForDate, ChoiceListForType, NextDiaryDate, SaveDay, ReadingsLeftForDay, SaveNewReadings

ME_RESOURCE_MAP = {
    DataForDate.URL: DataForDate,
    ChoiceListForType.URL: ChoiceListForType,
    NextDiaryDate.URL: NextDiaryDate,
    SaveDay.URL: SaveDay,
    ReadingsLeftForDay.URL: ReadingsLeftForDay,
    SaveNewReadings.URL: SaveNewReadings
}