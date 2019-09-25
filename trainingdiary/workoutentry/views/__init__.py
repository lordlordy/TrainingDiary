from .workout_views import new_workout_view, WorkoutUpdateView, workouts_list_view, delete_workout_view
from .day_views import DayUpdateView, days_list_view, new_day_view
from .upload_views import import_export, data_export, data_import
from .eddington_view import eddington_view, popular_eddington_view
from .graph_view import graph_view, popular_graph_view, popular_selected_in_graph_view
from .training_diary import summary_view
from .data_warehouse import (data_warehouse_update, warehouse_management, calculate_hrv, update_days, calculate_tsb,
                             interpolate_values)
from .reading_views import ReadingUpdateView, new_reading_view, delete_reading_view
from .race_result_views import race_results_list_view, RaceResultUpdateView, RaceResultDeleteView, new_race_result_view

