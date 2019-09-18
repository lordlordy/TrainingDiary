from django.urls import path
from . import views
#
urlpatterns = [
    path('', views.home_view, name='home'),
    # path('results/ironman', views.ironman_results_view, name='ironman_results'),
    # path('results/swimrun', views.swimrun_results_view, name='swimrun_results'),
    # path('results/races', views.race_results_view, name='race_results'),
    # path('results/all', views.all_results_view, name='all_results'),
]