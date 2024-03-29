import dateutil.parser
from django.http import JsonResponse

from workoutentry.modelling.modelling_types import WorkoutFloatMeasureEnum, ReadingEnum, PandasPeriod, Aggregation, DayAggregation, PandasInterpolation
from workoutentry.modelling.processor import TimeSeriesProcessor
from workoutentry.training_data import TrainingDataManager
from workoutentry.views.json.response import TrainingDiaryResponse
from workoutentry.views.training_diary_resource import TrainingDiaryResource


class ChoiceListForType(TrainingDiaryResource):

    URL = '/field/choices/'

    def required_post_fields(self):
        return ['type', 'include_all']

    def call_resource(self, request):
        type = request.POST['type']
        tdm = TrainingDataManager()

        choices = list()
        if type == 'activity':
            choices = tdm.activities()
        elif type == 'activityType':
            choices = tdm.activity_types()
        elif type == 'equipment':
            choices = tdm.equipment_types()
        elif type == 'tssMethod':
            choices = tdm.tss_methods()
        elif type == 'dayType':
            choices = tdm.day_types()
        elif type == 'measure':
            choices = [m.value for m in WorkoutFloatMeasureEnum] + [m.value for m in ReadingEnum]
        elif type == 'generated_measure':
            choices = [m for m in TimeSeriesProcessor.generated_measures()]
        elif type == 'period':
            choices = [p.value for p in PandasPeriod]
        elif type == 'aggregation':
            choices = [a.value for a in Aggregation]
        elif type == 'day_aggregation':
            choices = [a.value for a in DayAggregation]
        elif type == 'years':
            choices = range(dateutil.parser.parse(tdm.earliest_date()).year, dateutil.parser.parse(tdm.latest_date()).year + 1)
        elif type == 'processor':
            choices = TimeSeriesProcessor.TYPES
        elif type == 'interpolation':
            choices = [i.value for i in PandasInterpolation]

        if request.POST['include_all'] == 'true':
            choices.append('All')

        response = TrainingDiaryResponse()
        response.add_data('choices', sorted([{'text': c, 'id': c} for c in choices], key=lambda c: c["text"]))

        return JsonResponse(data=response.as_dict())