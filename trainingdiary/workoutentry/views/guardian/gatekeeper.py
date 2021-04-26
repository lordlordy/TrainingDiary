import logging

from django.http import JsonResponse

from workoutentry.views.guardian.anyone import ANYONE_RESOURCE_MAP
from workoutentry.views.guardian.me import ME_RESOURCE_MAP
from workoutentry.views.json.response import TrainingDiaryResponse

logger = logging.getLogger(__name__)


def check_and_forward(request):

    resource = request.POST.get("resource", None)

    if resource is None:
        return JsonResponse(data=TrainingDiaryResponse.error_response_dict("No resource specifiec"))

    logger.debug(f"{request.user} requesting {resource}")

    if request.user.is_authenticated:
        view_class = ME_RESOURCE_MAP.get(resource, None)
    else:
        view_class = ANYONE_RESOURCE_MAP.get(resource, None)

    if view_class is None:
        # todo - this is temporary until get authentication in place
        view_class = ME_RESOURCE_MAP.get(resource, None)
        if view_class is None:
            return JsonResponse(data=TrainingDiaryResponse.error_response_dict(f"Cannot process request as no resource for {resource}"))

    view_class_instance = view_class()
    missing_fields = []
    for field in view_class_instance.required_post_fields():
        if field not in request.POST:
            missing_fields.append(field)
    for field in view_class_instance.required_file_fields():
        if field not in request.FILES:
            missing_fields.append(field)

    if len(missing_fields) > 0:
        return JsonResponse(data=TrainingDiaryResponse.error_response_dict(f'Cannot process {resource} as was not passed all these fields: {", ".join(missing_fields)}'))

    response = view_class_instance.call_resource(request)

    return response