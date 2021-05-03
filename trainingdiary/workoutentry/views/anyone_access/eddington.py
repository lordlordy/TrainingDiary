from django.http import JsonResponse

from workoutentry.modelling.data_definition import DataDefinition, SeriesDefinition
from workoutentry.modelling.eddington import EddingtonNumberProcessor, AnnualEddingtonNumberProcessor, MonthlyEddingtonNumberProcessor
from workoutentry.modelling.modelling_types import DayAggregation, Aggregation, PandasPeriod
from workoutentry.modelling.period import Period
from workoutentry.modelling.rolling import RollingDefinition, NoOpRoller
from workoutentry.modelling.time_series import TimeSeriesManager
from workoutentry.training_data import TrainingDataManager
from workoutentry.views.json.response import TrainingDiaryResponse
from workoutentry.views.utilities.utilities import BaseJSONForm


class EddingtonNumberCalculation(BaseJSONForm):

    URL = "/eddington/calculation/"

    def required_post_fields(self):
        return ['json']

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
                                         month=dd['month'])

        dd_keys.remove('activity')
        dd_keys.remove('activity_type')
        dd_keys.remove('equipment')
        dd_keys.remove('measure')
        dd_keys.remove('day_aggregation')
        dd_keys.remove('day_type')
        dd_keys.remove('day_of_week')
        dd_keys.remove('month')

        period = Period(label=PandasPeriod(dd['period']), aggregation=Aggregation(dd['period_aggregation']),
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

        processor = None
        if dd['eddington_type'] == 'Lifetime':
            processor = EddingtonNumberProcessor()
        elif dd['eddington_type'] == 'Annual':
            processor = AnnualEddingtonNumberProcessor()
        elif dd['eddington_type'] == 'Monthly':
            processor = MonthlyEddingtonNumberProcessor()

        response = TrainingDiaryResponse()
        [response.add_message(response.MSG_ERROR, e) for e in errors]

        if processor is not None:
            tss = TimeSeriesManager.TimeSeriesSet(data_definition, series_definition=series_definition, processor=processor)
            ts = TimeSeriesManager().time_series(TrainingDataManager().diary_time_period(), [tss])
            response.add_data('time_series', ts)

        response.add_data('unused_data', [k for k in dd_keys])

        return JsonResponse(data=response.as_dict())
