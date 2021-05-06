from django.urls import path
from workoutentry.views.home import home

urlpatterns = [

    path('', home, name='home'),

]