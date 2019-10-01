from django.urls import path
from studentTSB.views import (home_view, player_list_view, coach_list_view, event_list_view, team_list_view, team_view,
                              event_edit_view, event_save_view, player_edit_view, player_save_view, team_update_view,
                              new_team_view, coach_edit_view, coach_save_view, event_generate_view,
                              add_players_to_team_view, add_coaches_to_team_view, delete_player_from_team,
                              delete_coach_from_team, delete_event_from_team)

from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', home_view, name='home'),
    path('players/list/', player_list_view, name='player_list'),
    path('players/edit/<int:id>/', player_edit_view, name='player_edit'),
    path('players/new/', player_edit_view, name='player_new'),
    path('players/save/', player_save_view, name='player_save'),
    path('coaches/list/', coach_list_view, name='coach_list'),
    path('coaches/edit/<int:id>/', coach_edit_view, name='coach_edit'),
    path('coaches/new/', coach_edit_view, name='coach_new'),
    path('coaches/save/', coach_save_view, name='coach_save'),
    path('events/list/', event_list_view, name='event_list'),
    path('events/edit/<int:team_id>/<int:id>/', event_edit_view, name='event_edit'),
    path('events/save/', event_save_view, name='event_save'),
    path('events/generate/<int:id>', event_generate_view, name='event_generate'),
    path('teams/list/', team_list_view, name='team_list'),
    path('teams/edit/<int:id>', team_view, name='team_edit'),
    path('teams/add/player/<int:id>', add_players_to_team_view, name='team_add_player'),
    path('teams/remove/player/<int:team_id>/<int:player_id>/', delete_player_from_team, name='team_remove_player'),
    path('teams/add/coach/<int:id>', add_coaches_to_team_view, name='team_add_coach'),
    path('teams/remove/coach/<int:team_id>/<int:coach_id>/', delete_coach_from_team, name='team_remove_coach'),
    path('teams/add/event/<int:team_id>', event_edit_view, name='event_new'),
    path('teams/remove/event/<int:team_id>/<int:event_id>/', delete_event_from_team, name='event_remove'),
    path('teams/update/', team_update_view, name='team_update'),
    path('teams/new/', new_team_view, name='team_new'),
]
