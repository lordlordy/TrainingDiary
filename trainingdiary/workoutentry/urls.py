from django.urls import path
from workoutentry.views import (eddington_view, popular_eddington_view,
                                graph_view, popular_graph_view, popular_selected_in_graph_view,
                                summary_view, race_results_list_view, RaceResultUpdateView, RaceResultDeleteView,
                                days_list_view, DayUpdateView, new_day_view, new_race_result_view,
                                workouts_list_view, WorkoutUpdateView, new_workout_view, delete_workout_view,
                                ReadingUpdateView, new_reading_view, delete_reading_view,
                                import_export, data_import, data_export,
                                data_warehouse_update, warehouse_management, calculate_hrv, update_days, calculate_tsb,
                                interpolate_values)
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', eddington_view, name='eddington_numbers'),
    path('days/', login_required(days_list_view), name='day_list'),
    path('days/new/', login_required(new_day_view), name='day_new'),
    path('days/update/<str:date>/', login_required(DayUpdateView.as_view()), name='day_form'),
    path('workouts/', login_required(workouts_list_view), name='workout_list'),
    path('workouts/new/<str:date>', login_required(new_workout_view), name='workout_new'),
    path('workouts/update/<str:date>/<int:workout_number>/', login_required(WorkoutUpdateView.as_view()), name='workout_form'),
    path('workouts/delete/<str:date>/<int:workout_number>/', login_required(delete_workout_view), name='workout_delete'),
    path('race_results/', login_required(race_results_list_view), name='race_result_list'),
    path('race_results/new/', login_required(new_race_result_view), name='race_result_new'),
    path('race_results/update/<str:date>/<int:race_number>/', login_required(RaceResultUpdateView.as_view()), name='race_result_form'),
    path('race_results/delete/<str:date>/<int:race_number>/', login_required(RaceResultDeleteView.as_view()), name='race_result_delete'),
    path('readings/new/<str:date>/', login_required(new_reading_view), name='reading_new'),
    path('readings/update/<str:date>/<str:type>/', login_required(ReadingUpdateView.as_view()), name='reading_form'),
    path('readings/delete_reading_view/<str:date>/<str:type>', login_required(delete_reading_view), name='reading_delete'),
    path('diary/import_export/', login_required(import_export), name='diary_import_export'),
    path('diary/import_export/import/', login_required(data_import), name='diary_import'),
    path('diary/import_export/export/', login_required(data_export), name='diary_export'),
    path('data_warehouse/management/', login_required(warehouse_management), name='date_warehouse_management'),
    path('data_warehouse/update/', login_required(data_warehouse_update), name='date_warehouse_update'),
    path('data_warehouse/generate/days/', login_required(update_days), name='update_days'),
    path('data_warehouse/generate/tsb/', login_required(calculate_tsb), name='calculate_tsb'),
    path('data_warehouse/generate/interpolate/', login_required(interpolate_values), name='interpolate_values'),
    path('data_warehouse/generate/hrv/', login_required(calculate_hrv), name='calculate_hrv'),
    path('eddington/', eddington_view, name='eddington_numbers'),
    path('eddington/simple', popular_eddington_view, name='eddington_numbers_simple'),
    path('graphs/', graph_view, name='graphs'),
    path('graphs/select/popular', popular_selected_in_graph_view, name='graphs_popular_selected'),
    path('graphs/popular/', popular_graph_view, name='popular_graphs'),
    path('training_diary/summary/', summary_view, name='training_diary_summary'),

]
