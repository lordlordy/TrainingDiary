from django.http import JsonResponse

from workoutentry.training_data import TrainingDataManager
from workoutentry.views.json.response import TrainingDiaryResponse
from workoutentry.views.training_diary_resource import TrainingDiaryResource


class DataForDate(TrainingDiaryResource):

    URL = '/data/for_date/'

    def required_post_fields(self):
        return ['date']

    def call_resource(self, request):
        response = TrainingDiaryResponse()
        tdm = TrainingDataManager()

        day = tdm.day_for_date(request.POST['date'])

        response.add_data('Day', day.json_dictionary())

        return JsonResponse(data=response.as_dict())


class ChoiceListForType(TrainingDiaryResource):

    URL = '/field/choices/'

    def required_post_fields(self):
        return ['type']

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

        response = TrainingDiaryResponse()
        response.add_data('choices', sorted([{'text': c, 'id': c} for c in choices], key=lambda c: c["text"]))

        return JsonResponse(data=response.as_dict())
