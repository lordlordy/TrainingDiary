from django.urls import path
from studentTSB.views import (home_view,
                              player_list_view,
                              coach_list_view,
                              event_list_view,
                              team_list_view,
                              team_view,
                              team_event_occurrence_list_view,
                              remove_team_from_event,
                              event_edit_view,
                              event_save_view,
                              delete_event,
                              player_edit_view,
                              player_save_view,
                              team_update_view,
                              new_team_view,
                              coach_edit_view,
                              coach_save_view,
                              add_teams_to_coach_view,
                              event_generate_team_view,
                              event_generate_player_view,
                              event_occurrence_view,
                              player_event_occurrence_from_player_view,
                              player_event_occurrence_from_event_view,
                              player_event_occurrence_from_event_occurrence_view,
                              update_player_event_occurrence,
                              update_all_player_event_duration,
                              update_all_player_event_rpe,
                              update_all_player_event_state,
                              update_all_player_event_comments,
                              add_teams_to_player_view,
                              add_players_to_team_view,
                              add_coaches_to_team_view,
                              delete_player_from_team,
                              remove_team_from_player,
                              delete_coach_from_team,
                              delete_event_from_team,
                              player_personal_training_view,
                              reading_type_list_view,
                              reading_type_edit,
                              reading_type_update,
                              reading_edit,
                              reading_update,
                              delete_reading,
                              add_teams_to_event_view,
                              event_occurrence_states_list_view,
                              new_event_occurrence_state,
                              update_event_occurrence_state,
                              delete_event_occurrence_state)

from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', home_view, name='home'),
    path('players/list/', player_list_view, name='player_list'),
    path('players/edit/<int:id>/', player_edit_view, name='player_edit'),
    path('players/new/', player_edit_view, name='player_new'),
    path('players/save/', player_save_view, name='player_save'),
    path('players/add/teams/<int:id>/', add_teams_to_player_view, name='add_teams_to_player'),
    path('players/remove/team/<int:player_id>/<int:team_id>/', remove_team_from_player, name='remove_team_from_player'),
    path('players/add/personal_training/<int:player_id>/', player_personal_training_view, name='player_personal_training'),
    path('players/event/occurrence/<int:id>/<int:player_id>/', player_event_occurrence_from_player_view,
         name='player_event_occurrence_from_player_view'),
    path('players/reading/edit/<int:id>/', reading_edit, name='reading_edit'),
    path('players/reading/new/<int:player_event_occurrence_id>/', reading_edit, name='reading_new'),
    path('players/reading/update/', reading_update, name='reading_update'),
    path('players/reading/delete/<int:id>/', delete_reading, name='delete_reading'),
    path('coaches/list/', coach_list_view, name='coach_list'),
    path('coaches/edit/<int:id>/', coach_edit_view, name='coach_edit'),
    path('coaches/new/', coach_edit_view, name='coach_new'),
    path('coaches/save/', coach_save_view, name='coach_save'),
    path('coaches/add/teams/<int:id>/', add_teams_to_coach_view, name='add_teams_to_coach'),
    path('events/list/', event_list_view, name='event_list'),
    path('events/edit/<int:id>/', event_edit_view, name='event_edit'),
    path('events/save/', event_save_view, name='event_save'),
    path('events/new/', event_edit_view, name='event_new'),
    path('events/delete/<int:event_id>/', delete_event, name='delete_event'),
    path('events/add/teams/<int:id>/', add_teams_to_event_view, name='event_add_teams'),
    path('events/remove/team/<int:team_id>/<int:event_id>/', remove_team_from_event, name='remove_team_from_event'),
    path('events/generate/team/<int:id>/', event_generate_team_view, name='event_generate_team'),
    path('events/generate/player/<int:id>/', event_generate_player_view, name='event_generate_player'),
    path('events/occurrence/list/', team_event_occurrence_list_view, name='team_event_occurrence_list'),
    path('events/occurrence/edit/<int:id>/<str:date>/', event_occurrence_view, name='event_occurrence'),
    path('events/occurrence/edit/all/duration/<int:id>/<str:date>/', update_all_player_event_duration, name='update_all_player_event_duration'),
    path('events/occurrence/edit/all/rpe/<int:id>/<str:date>/', update_all_player_event_rpe, name='update_all_player_event_rpe'),
    path('events/occurrence/edit/all/state/<int:id>/<str:date>/', update_all_player_event_state, name='update_all_player_event_state'),
    path('events/occurrence/edit/all/comments/<int:id>/<str:date>/', update_all_player_event_comments, name='update_all_player_event_comments'),
    path('events/occurrence/edit/player/<int:id>/<str:date>/', update_player_event_occurrence,
         name='update_player_event_occurrence'),
    path('events/occurrence/player/<int:id>/<int:event_id>/<str:date>/',
         player_event_occurrence_from_event_occurrence_view, name='player_event_occurrence_from_event_occurrence_view'),
    path('events/player/occurrence/<int:id>/<int:event_id>/', player_event_occurrence_from_event_view,
         name='player_event_occurrence_from_event_view'),
    path('teams/list/', team_list_view, name='team_list'),
    path('teams/edit/<int:id>/', team_view, name='team_edit'),
    path('teams/add/player/<int:id>/', add_players_to_team_view, name='team_add_player'),
    path('teams/remove/player/<int:team_id>/<int:player_id>/', delete_player_from_team, name='team_remove_player'),
    path('teams/add/coach/<int:id>/', add_coaches_to_team_view, name='team_add_coach'),
    path('teams/remove/coach/<int:team_id>/<int:coach_id>/', delete_coach_from_team, name='team_remove_coach'),
    path('teams/add/event/<int:team_id>/', event_edit_view, name='event_new'),
    path('teams/remove/event/<int:team_id>/<int:event_id>/', delete_event_from_team, name='event_remove'),
    path('teams/update/', team_update_view, name='team_update'),
    path('teams/new/', new_team_view, name='team_new'),
    path('admin/reading_types/list/', reading_type_list_view, name='reading_types'),
    path('admin/reading_types/edit/<int:id>/', reading_type_edit, name='reading_type_edit'),
    path('admin/reading_types/update/', reading_type_update, name='reading_type_update'),
    path('admin/reading_types/new/', reading_type_edit, name='reading_type_new'),
    path('admin/event_occurrence_states/list/', event_occurrence_states_list_view, name='event_occurrence_states'),
    path('admin/event_occurrence_states/new/', new_event_occurrence_state, name='event_occurrence_state_new'),
    path('admin/event_occurrence_states/update/<int:id>/', update_event_occurrence_state,
         name='event_occurrence_state_update'),
    path('admin/event_occurrence_states/delete/<int:state_id>/', delete_event_occurrence_state,
         name='event_occurrence_state_delete'),

]
