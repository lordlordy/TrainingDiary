from django.urls import path
from workoutentry.views.home import home
from workoutentry.views.login import force_csrf_cookie_set

urlpatterns = [

    path('', home, name='home'),
    path('force/csrf/', force_csrf_cookie_set),

]