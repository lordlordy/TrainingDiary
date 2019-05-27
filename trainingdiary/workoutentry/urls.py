from django.urls import path
from . import views

from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', views.eddington_view, name='eddington_numbers'),
    path('days/', login_required(views.days_list_view), name='day_list'),
    path('days/<int:pk>/', login_required(views.DayUpdateView.as_view()), name='day_form'),
    path('days/new/', login_required(views.DayCreateView.as_view()), name='day_new'),
    path('workouts/', login_required(views.workouts_list_view), name='workout_list'),
    path('workouts/<int:pk>/', login_required(views.WorkoutUpdateView.as_view()), name='workout_form'),
    path('workouts/new/<int:day_pk>', login_required(views.WorkoutCreateView.as_view()), name='workout_new'),
    path('dairy/upload/', login_required(views.diary_upload), name='diary_upload'),
    path('eddington/', views.eddington_view, name='eddington_numbers'),
    # path('accounts/profile/', views.eddington_view, name='eddington_numbers'),
    path('graphs/', views.graph_view, name='graphs'),

] #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
