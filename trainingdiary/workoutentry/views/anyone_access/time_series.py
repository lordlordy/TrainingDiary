from django.http import JsonResponse

from workoutentry.modelling.data_definition import DataDefinition, SeriesDefinition
from workoutentry.modelling.modelling_types import DayAggregation, Aggregation, PandasPeriod
from workoutentry.modelling.period import Period
from workoutentry.modelling.processor import NoOpProcessor, TimeSeriesProcessor
from workoutentry.modelling.rolling import RollingDefinition, NoOpRoller
from workoutentry.modelling.time_period import TimePeriod
from workoutentry.modelling.time_series import TimeSeriesManager
from workoutentry.training_data import TrainingDataManager
from workoutentry.views.json.response import TrainingDiaryResponse
from workoutentry.views.utilities.utilities import BaseJSONForm


class TimeSeriesAccess(BaseJSONForm):

    URL = "/time_series/"

    def required_post_fields(self):
        return ['json']

    def _date_fields(self) -> set:
        return {'series_start', 'series_end'}

    def call_resource(self, request):
        dd, errors = self._process_data(request.POST['json'])

        dd_keys = set([d for d in dd.keys()])

        data_definition = DataDefinition(activity=dd['activity'],
                                         activity_type=dd['activity_type'],
                                         equipment=dd['equipment'],
                                         measure=dd['measure'],
                                         day_aggregation_method=DayAggregation(dd['day_aggregation']),
                                         day_type=dd['day_type'],
                                         day_of_week=dd['day_of_week'],
                                         month=dd['month'],
                                         interpolation=dd['interpolation'])

        dd_keys.remove('activity')
        dd_keys.remove('activity_type')
        dd_keys.remove('equipment')
        dd_keys.remove('measure')
        dd_keys.remove('day_aggregation')
        dd_keys.remove('day_type')
        dd_keys.remove('day_of_week')
        dd_keys.remove('month')
        dd_keys.remove('interpolation')

        period = Period(pandas_period=PandasPeriod(dd['period']), aggregation=Aggregation(dd['period_aggregation']),
                        to_date=dd['to_date'] == 'yes',
                        incl_zeroes=dd['period_include_zeroes'] == 'yes')
        dd_keys.remove('period')
        dd_keys.remove('period_aggregation')
        dd_keys.remove('to_date')
        dd_keys.remove('period_include_zeroes')

        if dd['rolling'] == 'yes':
            rolling_definition = RollingDefinition(periods=int(dd['number_of_rolling_periods']), aggregation=Aggregation(dd['rolling_aggregation']),
                                                   incl_zeros=dd['rolling_include_zeroes'] == 'yes')
        else:
            rolling_definition = NoOpRoller()
        dd_keys.remove('number_of_rolling_periods')
        dd_keys.remove('rolling_aggregation')
        dd_keys.remove('rolling_include_zeroes')
        dd_keys.remove('rolling')

        series_definition = SeriesDefinition(period=period, rolling_definition=rolling_definition)

        processor = self.get_processor(dd)
        dd_keys.remove('processor_type')

        response = TrainingDiaryResponse()
        [response.add_message(response.MSG_ERROR, e) for e in errors]

        diary_time_period = TrainingDataManager().diary_time_period()
        data_tp = TimePeriod(diary_time_period.start if dd['series_start'] is None else dd['series_start'],
                             diary_time_period.end if dd['series_end'] is None else dd['series_end'])
        dd_keys.remove('series_start')
        dd_keys.remove('series_end')

        tss = TimeSeriesManager.TimeSeriesSet(data_definition, series_definition=series_definition, processor=processor)
        ts = TimeSeriesManager().time_series_graph(data_tp, [tss])
        response.add_data('time_series', ts)

        if len(dd_keys) > 0:
            response.add_message(response.MSG_WARNING, f"The following data was not used: {' ,'.join(dd_keys)}")

        return JsonResponse(data=response.as_dict())

    def get_processor(self, dd):
        return TimeSeriesProcessor.get_processor(dd.get('processor_type', ""))
