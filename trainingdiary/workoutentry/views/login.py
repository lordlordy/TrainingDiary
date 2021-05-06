from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from workoutentry.views.json.response import TrainingDiaryResponse
from workoutentry.views.training_diary_resource import TrainingDiaryResource


@method_decorator([ensure_csrf_cookie], name='dispatch')
class TrainingDiaryLogin(LoginView):

    def post(self, request, *args, **kwargs):
        r = super().post(request, args, kwargs)
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return JsonResponse(data=TrainingDiaryResponse.error_response_dict('Invalid username and password. Please try again'))

        if r.status_code == 302:
            login(self.request, user)
            response = TrainingDiaryResponse()
            response.set_status(response.SUCCESS)
            response.add_data('user', str(user))
            response.add_data('logged_in', True)
            return JsonResponse(data=response.as_dict())
        else:
            return JsonResponse(data=TrainingDiaryResponse.error_response_dict('Unable to login. No idea why'))


class TrainingDiaryLogout(TrainingDiaryResource):

    URL = '/logout/'

    def call_resource(self, request):
        logout(request)
        response = TrainingDiaryResponse()
        response.set_status(response.SUCCESS)
        response.add_data('logged_in', False)
        return JsonResponse(data=response.as_dict())


@ensure_csrf_cookie
def force_csrf_cookie_set(request):
    print('force_csrf_cookie_set')
    return JsonResponse(data={'ok': 'yes'})
