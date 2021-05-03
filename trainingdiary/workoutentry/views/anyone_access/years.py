from datetime import date

from django.http import JsonResponse

from workoutentry.modelling.data_definition import DataDefinition, SeriesDefinition
from workoutentry.modelling.modelling_types import DayAggregation, PandasPeriod
from workoutentry.modelling.period import Period
from workoutentry.modelling.time_period import TimePeriod
from workoutentry.modelling.time_series import TimeSeriesManager
from workoutentry.views.json.response import TrainingDiaryResponse
from workoutentry.views.training_diary_resource import TrainingDiaryResource


class YearSummary(TrainingDiaryResource):

    URL = '/year/summary/'

    def required_post_fields(self):
        return ['year', 'period']

    def call_resource(self, request):
        response = TrainingDiaryResponse()
        year = int(request.POST['year'])
        tp = TimePeriod(date(year,1,1), date(year, 12,31))

        swim_km = DataDefinition(activity='Swim', activity_type='All', equipment='All', measure='km', day_aggregation_method=DayAggregation.SUM)
        bike_km = DataDefinition(activity='Bike', activity_type='All', equipment='All', measure='km', day_aggregation_method=DayAggregation.SUM)
        run_km = DataDefinition(activity='Run', activity_type='All', equipment='All', measure='km', day_aggregation_method=DayAggregation.SUM)
        hours = DataDefinition(activity='All', activity_type='All', equipment='All', measure='hours', day_aggregation_method=DayAggregation.SUM)
        series_defn = SeriesDefinition(period=Period(PandasPeriod(request.POST['period'])))

        tss_list = list()
        tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=swim_km, series_definition=series_defn))
        tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=bike_km, series_definition=series_defn))
        tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=run_km, series_definition=series_defn))
        tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=hours, series_definition=series_defn))

        dd = TimeSeriesManager().time_series_list(tp, tss_list)
        response.add_data('time_series', dd)

        return JsonResponse(data=response.as_dict())