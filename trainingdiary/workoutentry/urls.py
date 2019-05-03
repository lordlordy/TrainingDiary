from django.urls import path
from . import views

urlpatterns = [
    path('workouts/', views.WorkoutListView.as_view(), name='workout_list'),
    path('workouts/<int:pk>/', views.WorkoutUpdateView.as_view(), name='workout_form'),
    path('workouts/new/', views.WorkoutCreateView.as_view(), name='workout_new'),

]