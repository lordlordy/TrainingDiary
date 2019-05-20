from django.urls import path
from . import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.days_list_view, name='eddington_numbers'),
    path('days/', views.days_list_view, name='day_list'),
    path('days/<int:pk>/', views.DayUpdateView.as_view(), name='day_form'),
    path('days/new/', views.DayCreateView.as_view(), name='day_new'),
    path('workouts/', views.workouts_list_view, name='workout_list'),
    path('workouts/<int:pk>/', views.WorkoutUpdateView.as_view(), name='workout_form'),
    path('workouts/new/<int:day_pk>', views.WorkoutCreateView.as_view(), name='workout_new'),
    path('dairy/upload/', views.diary_upload, name='diary_upload'),
    path('eddington/', views.eddington_view, name='eddington_numbers'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)