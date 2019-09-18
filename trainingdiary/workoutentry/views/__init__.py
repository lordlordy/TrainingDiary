from .workout_views import WorkoutCreateView, WorkoutUpdateView, workouts_list_view, WorkoutDeleteView
from .day_views import DayCreateView, DayUpdateView, days_list_view
from .upload_views import diary_upload
from .eddington_view import eddington_view, popular_eddington_view
from .graph_view import graph_view, popular_graph_view
from .training_diary import summary_view
from .data_warehouse import data_warehouse_update
from .reading_views import ReadingUpdateView
from .race_result_views import race_results_list_view, RaceResultUpdateView