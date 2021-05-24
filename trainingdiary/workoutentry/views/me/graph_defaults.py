from django.http import JsonResponse

from workoutentry.graphs.defaults_db import ChartDefaultsManager
from workoutentry.modelling.data_definition import SeriesDefinition
from workoutentry.modelling.modelling_types import PandasPeriod, Aggregation
from workoutentry.modelling.period import Period
from workoutentry.modelling.rolling import NoOpRoller, RollingDefinition
from workoutentry.views.json.response import TrainingDiaryResponse
from workoutentry.views.training_diary_resource import TrainingDiaryResource
from workoutentry.views.utilities.utilities import BaseJSONForm


class GetGraphDefaults(TrainingDiaryResource):

    URL = '/graph/defaults/'

    def call_resource(self, request):
        cdm = ChartDefaultsManager()
        defaults = cdm.get_defaults()
        response = TrainingDiaryResponse()
        response.add_data('defaults', [d.data_dictionary() for d in defaults])

        return JsonResponse(data=response.as_dict())


class DeleteGraphDefaults(TrainingDiaryResource):

    URL = '/graph/defaults/delete/'

    def required_post_fields(self):
        return ['unique_key']

    def call_resource(self, request):
        cdm = ChartDefaultsManager()
        cdm.delete_defaults(request.POST['unique_key'])
        response = TrainingDiaryResponse()
        response.add_message(response.MSG_INFO, f"Defaults deleted: {request.POST['unique_key']}")
        response.add_data('deleted_unique_key', request.POST['unique_key'])
        return JsonResponse(data=response.as_dict())


class SaveGraphDefaults(BaseJSONForm):

    URL = '/graph/defaults/save/'

    def required_post_fields(self):
        return ['json']

    def call_resource(self, request):
        response = TrainingDiaryResponse()
        dd, errors = self._process_data(request.POST['json'])

        if 'unique_key' in dd and dd['unique_key'] != 'none' and dd['unique_key'] != '':
            unique_key = dd['unique_key']
        else:
            unique_key = self.calculate_unique_key(dd)

        cdm = ChartDefaultsManager()
        cdm.save_defaults(unique_key=unique_key,
                          label=dd['label'],
                          chart_type=dd['chart_type'],
                          borderColor=dd['borderColor'],
                          backgroundColor=dd['backgroundColor'],
                          fill=1 if dd['fill'] == 'yes' else 0,
                          pointRadius=dd['pointRadius'],
                          pointHoverRadius=dd['pointHoverRadius'],
                          showLine=1 if dd['showLine'] == 'yes' else 0,
                          position=dd['position'],
                          number=dd['number'],
                          scale_type=dd['scale_type'],
                          draw_grid_lines=1 if dd['draw_grid_lines'] == 'yes' else 0
                          )

        defaults = cdm.get_default(unique_key=unique_key)

        [response.add_message(response.MSG_ERROR, e) for e in errors]
        response.add_data('defaults_added', [d.data_dictionary() for d in defaults])

        return JsonResponse(data=response.as_dict())

    def calculate_unique_key(self, dd):
        period = Period(pandas_period=PandasPeriod(dd['period']),
                        aggregation=Aggregation(dd['period_aggregation']),
                        to_date=dd['to_date'] == 'yes',
                        incl_zeroes=dd['period_include_zeroes'] == 'yes')
        if dd['rolling'] == 'no':
            rolling_definition = NoOpRoller()
        else:
            rolling_definition = RollingDefinition(periods=dd['number_of_periods'],
                                                   aggregation=Aggregation(dd['rolling_aggregation']),
                                                   incl_zeros=dd['rolling_include_zeroes'] == 'yes')
        measure = dd['measure'] if dd['timeseries_measure'] == 'noop' else dd['timeseries_measure']
        unique_key = SeriesDefinition.generate_unique_key(period, rolling_definition, measure, dd['measure'])
        return unique_key

    def _int_fields(self) -> set:
        return {}

    def _float_fields(self) -> set:
        return {}

    def _yes_no_boolean_fields(self) -> set:
        return {"can_record_for_day", "can_record_in_workout"}

    def _extra_processing(self, data) -> bool:
        return False
