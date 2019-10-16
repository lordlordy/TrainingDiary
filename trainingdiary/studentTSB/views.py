from django.shortcuts import render
from django.http import HttpResponseRedirect
from studentTSB.database import DatabaseManager, tsb_for_player, tsb_for_team
from studentTSB.forms import EventEditForm, PlayerEditForm, TeamEditForm, CoachEditForm, SelectForm


def home_view(request):
    return render(request, 'studentTSB/home.html')


def player_list_view(request):
    players = DatabaseManager().players()
    return render(request, 'studentTSB/player_list.html', {'players': players})


def coach_list_view(request):
    coaches = DatabaseManager().coaches()
    return render(request, 'studentTSB/coach_list.html', {'coaches': coaches})


def event_list_view(request):
    events = DatabaseManager().events()
    return render(request, 'studentTSB/event_list.html', {'events': events})


def team_list_view(request):
    teams = DatabaseManager().teams()
    return render(request, 'studentTSB/team_list.html', {'teams': teams, 'form': TeamEditForm()})


def new_team_view(request):
    if 'name' in request.POST:
        DatabaseManager().add_new_team(request.POST['name'])
    return team_list_view(request)


def team_view(request, **kwargs):
    dm = DatabaseManager()
    team = dm.team_for_id(kwargs['id'])
    initial_values = team.data_dictionary()

    potential_players = dm.players()
    player_id_dict = dict()
    for p in potential_players:
        player_id_dict[p.id] = p.name
    player_ids = set([p.id for p in potential_players]) - set([p.id for p in team.players])
    player_choices = [(i, player_id_dict[i]) for i in player_ids]
    add_player_form = SelectForm('Players', player_choices)

    potential_coaches = dm.coaches()
    coach_id_dict = dict()
    for c in potential_coaches:
        coach_id_dict[c.id] = c.name
    coach_ids = set([c.id for c in potential_coaches]) - set([c.id for c in team.coaches])
    coach_choices = [(i, coach_id_dict[i]) for i in coach_ids]
    add_coach_form = SelectForm('Coaches', coach_choices)

    file_name = f'team-{team.id}-TSB'
    tsb_for_team(team, file_name)

    return render(request, 'studentTSB/team.html', {'team': team,
                                                    'form': TeamEditForm(initial=initial_values),
                                                    'player_select_form': add_player_form,
                                                    'coach_select_form': add_coach_form,
                                                    'graph_img': f'tmp/{file_name}.png'})


def add_players_to_team_view(request, **kwargs):
    dm = DatabaseManager()
    for pid in request.POST.getlist('Players'):
        dm.add_player_to_team(pid, kwargs['id'])
    return team_view(request, **kwargs)


def add_coaches_to_team_view(request, **kwargs):
    dm = DatabaseManager()
    for cid in request.POST.getlist('Coaches'):
        dm.add_coach_to_team(cid, kwargs['id'])
    return team_view(request, **kwargs)


def team_update_view(request):
    DatabaseManager().update_team(request.POST['id'], request.POST['name'])
    kwargs = {'id': request.POST['id']}
    return team_view(request, **kwargs)


def event_edit_view(request, **kwargs):
    initial_values = dict()
    context = dict()
    if 'id' in kwargs:
        event = DatabaseManager().event_for_id(kwargs['id'])
        initial_values = event.data_dictionary()
        context['event'] = event

    context['team'] = DatabaseManager().team_for_id(kwargs['team_id'])
    initial_values['team_id'] = context['team'].id
    context['form'] = EventEditForm(initial=initial_values)

    return render(request, 'studentTSB/event_edit.html', context)

def event_generate_view(request, **kwargs):
    event = DatabaseManager().event_for_id(kwargs['id'])
    event.generate_occurrences()
    dd = {'id': kwargs['id'], 'team_id': event.team_id}
    return event_edit_view(request, **dd)


def event_save_view(request):
    dm = DatabaseManager()
    if 'id' in request.POST and request.POST['id'] != '':
        dm.update_event(request.POST['id'], request.POST['name'], request.POST['start_time'], request.POST['end_time'],
                        request.POST['estimated_rpe'], request.POST['start_date'], request.POST['end_date'],
                        request.POST['frequency'], request.POST['team_id'])
    else:
        event_id = dm.add_new_event(request.POST['name'], request.POST['start_time'], request.POST['end_time'],
                                    request.POST['estimated_rpe'], request.POST['start_date'], request.POST['end_date'],
                                    request.POST['frequency'], request.POST['team_id'])
        # generate occurrences for even when first saved
        event = dm.event_for_id(event_id)
        event.generate_occurrences()

    team = DatabaseManager().team_for_id(request.POST['team_id'])
    return HttpResponseRedirect(f'/studentTSB/teams/edit/{team.id}')


def player_edit_view(request, **kwargs):
    context = dict()
    if 'id' in kwargs:
        player = DatabaseManager().player_for_id(kwargs['id'])
        context['player'] = player
        initial_values = player.data_dictionary()
        context['player_name'] = player.name
        file_name = f'player-{player.id}-TSB'
        tsb_for_player(player, file_name)
        context['graph_img'] = f'tmp/{file_name}.png'
    else:
        initial_values = dict()
        context['player_name'] = "New Player"

    context['form'] = PlayerEditForm(initial=initial_values)

    return render(request, 'studentTSB/player_edit.html', context)


def player_save_view(request):
    if 'id' in request.POST and request.POST['id'] != '':
        DatabaseManager().update_player(request.POST['id'], request.POST['first_name'],
                                        request.POST['surname'], request.POST['known_as'],
                                        request.POST['email'], request.POST['dob'])
        kwargs = {'id': request.POST['id']}
        return player_edit_view(request, **kwargs)

    else:
        DatabaseManager().add_new_player(request.POST['first_name'], request.POST['surname'],
                                         request.POST['known_as'], request.POST['email'], request.POST['dob'])
        return player_list_view(request)


def add_teams_to_coach_view(request, **kwargs):
    dm = DatabaseManager()
    for tid in request.POST.getlist('Teams'):
        dm.add_coach_to_team(kwargs['id'], tid)

    return coach_edit_view(request, **kwargs)


def coach_edit_view(request, **kwargs):
    context = dict()
    if 'id' in kwargs:
        dm = DatabaseManager()
        coach = dm.coach_for_id(kwargs['id'])
        initial_values = coach.data_dictionary()
        context['coach_name'] = coach.name
        context['coach'] = coach
        all_teams = dm.teams()
        team_id_dict = dict()
        for t in all_teams:
            team_id_dict[t.id] = t.name
        team_ids = set([t.id for t in all_teams]) - set([t.id for t in coach.teams])
        team_choices = [(i, team_id_dict[i]) for i in team_ids]
        context['add_team_form'] = SelectForm('Teams', team_choices)
    else:
        initial_values = dict()
        context['coach_name'] = "New Coach"

    context['form'] = CoachEditForm(initial=initial_values)

    return render(request, 'studentTSB/coach_edit.html', context)


def coach_save_view(request):
    if 'id' in request.POST and request.POST['id'] != '':
        DatabaseManager().update_coach(request.POST['id'], request.POST['first_name'],
                                       request.POST['surname'], request.POST['known_as'], request.POST['email'])
        kwargs = {'id': request.POST['id']}
        return coach_edit_view(request, **kwargs)

    else:
        DatabaseManager().add_new_coach(request.POST['first_name'], request.POST['surname'],
                                        request.POST['known_as'], request.POST['email'])
        return coach_list_view(request)


def delete_player_from_team(request, **kwargs):
    dm = DatabaseManager()
    if request.method == "GET":
        player = dm.player_for_id(kwargs['player_id'])
        team = dm.team_for_id(kwargs['team_id'])
        return render(request, 'studentTSB/confirm_delete.html',
                      {'object': f"Player {player.name} from  {team.name}"})
    if request.method == "POST":
        dm.remove_player_from_team(kwargs['player_id'], kwargs['team_id'])
        return HttpResponseRedirect(f'/studentTSB/teams/edit/{kwargs["team_id"]}')


def delete_coach_from_team(request, **kwargs):
    dm = DatabaseManager()
    if request.method == "GET":
        coach = dm.coach_for_id(kwargs['coach_id'])
        team = dm.team_for_id(kwargs['team_id'])
        return render(request, 'studentTSB/confirm_delete.html',
                      {'object': f"Coach {coach.name} from  {team.name}"})
    if request.method == "POST":
        dm.remove_coach_from_team(kwargs['coach_id'], kwargs['team_id'])
        return HttpResponseRedirect(f'/studentTSB/teams/edit/{kwargs["team_id"]}')


def delete_event_from_team(request, **kwargs):
    dm = DatabaseManager()
    if request.method == "GET":
        event = dm.event_for_id(kwargs['event_id'])
        return render(request, 'studentTSB/confirm_delete.html',
                      {'object': f"Event {event.name} and all associated training sessions"})
    if request.method == "POST":
        dm.remove_event_for_id(kwargs['event_id'])
        return HttpResponseRedirect(f'/studentTSB/teams/edit/{kwargs["team_id"]}')
