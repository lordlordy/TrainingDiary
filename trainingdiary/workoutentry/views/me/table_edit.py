from django.http import JsonResponse

from workoutentry.training_data import TrainingDataManager
from workoutentry.views.utilities.utilities import parse_post_dictionary


def table_edit_reading(request):

    action = request.POST.get('action', None)
    if action == 'edit':
        return edit_reading(request.POST)
    elif action == 'remove':
        return JsonResponse(data={'error': "delete not implemented"})
    else:
        return JsonResponse(data={'error': "invalid action"})


def edit_reading(post_dictionary):

    models_dict = parse_post_dictionary(post_dictionary)
    tdm = TrainingDataManager()
    response_dict = dict()
    data = list()
    field_errors_list = list()
    primary_key = None
    for k, v in models_dict.items():
        primary_key = k
        for field, value in v.items():
            if field == 'value':
                tdm.update_reading_for_primary_key(k,value)
            else:
                field_errors_list.append({'name': 'value', 'status': f"invalid field name: {field}"})

    if primary_key is not None:
        reading = tdm.reading_for_primary_key(primary_key)
        data.append(reading.data_dictionary())
    else:
        response_dict['error'] = "No primary key"

    if len(data) > 0:
        response_dict['data'] = data
    if len(field_errors_list) > 0:
        response_dict['fieldErrors'] = field_errors_list

    return JsonResponse(data=response_dict)


