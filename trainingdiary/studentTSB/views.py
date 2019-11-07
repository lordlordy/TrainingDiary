from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from studentTSB.database import DatabaseManager, tsb_for_player, tsb_for_team, occurrence_states
from studentTSB.forms import (EventEditForm, PlayerEditForm, TeamEditForm, CoachEditForm, SelectForm,
                              PlayerEventOccurrenceForm, PersonalTrainingForm, ReadingTypeEditForm, ReadingEditForm,
                              EventOccurrenceStatusEditForm, SelectSingleForm)
from datetime import datetime


def home_view(request):
    return render(request, 'studentTSB/home.html')


def reading_type_list_view(request):
    reading_types = DatabaseManager().reading_types()
    return render(request, 'studentTSB/reading_types_list.html', {'reading_types': reading_types})


def event_occurrence_states_list_view(request):
    states = DatabaseManager().event_occurrence_states()
    return render(request, 'studentTSB/event_occurrence_states_list.html',
                  {'states': states, 'form': EventOccurrenceStatusEditForm()})


def team_event_occurrence_list_view(request):
    events = DatabaseManager().events()
    data = list()
    for e in events:
        for s in e.events_summary:
            summary = {'date': s[0], 'teams': s[1], 'event': e}
            data.append(summary)

    return render(request, 'studentTSB/team_event_occurrence_list.html', {'data': data})


def new_event_occurrence_state(request):
    if 'name' in request.POST:
        DatabaseManager().add_event_occurrence_state(request.POST['name'], 1)
    return event_occurrence_states_list_view(request)


def update_event_occurrence_state(request, **kwargs):
    if 'id' in kwargs and 'name' in request.POST and 'state' in request.POST:
        DatabaseManager().update_event_occurrence_state(kwargs['id'], request.POST['name'], request.POST['state'])
    return event_occurrence_states_list_view(request)


def delete_event_occurrence_state(request, **kwargs):
    dm = DatabaseManager()
    if request.method == "GET":
        state = dm.event_occurrence_state_for_id(kwargs['state_id'])
        return render(request, 'studentTSB/confirm_delete.html',
                      {'object': f"State {state.name}"})
    if request.method == "POST":
        dm.delete_event_occurrence_state(kwargs['state_id'])
        return HttpResponseRedirect(f'/studentTSB/admin/event_occurrence_states/list/')


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

    current_time = datetime.now().time().strftime("%H%M%S")
    file_name = f'team-{team.id}-TSB-{current_time}'
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


def add_teams_to_event_view(request, **kwargs):
    dm = DatabaseManager()
    for tid in request.POST.getlist('Teams'):
        dm.add_team_to_event(tid, kwargs['id'])
    return event_edit_view(request, **kwargs)


def event_edit_view(request, **kwargs):
    dm = DatabaseManager()
    initial_values = dict()
    context = dict()
    current_teams = set()
    if 'id' in kwargs:
        event = dm.event_for_id(kwargs['id'])
        initial_values = event.data_dictionary()
        context['event'] = event
        current_teams = set([t.id for t in event.teams])
    if 'team_id' in kwargs:
        initial_values['team_id'] = kwargs['team_id']

    potential_teams = dm.teams()
    team_id_dict = dict()
    for t in potential_teams:
        team_id_dict[t.id] = t.name
    team_ids = set([t.id for t in potential_teams]) - current_teams
    team_choices = [(i, team_id_dict[i]) for i in team_ids]
    context['select_team_form'] = SelectForm('Teams', team_choices)
    event_form = EventEditForm(initial=initial_values)
    context['form'] = event_form
    if 'id' in kwargs:
        event = dm.event_for_id(kwargs['id'])
        if not event.can_delete:
            event_form.fields['start_date'].widget.attrs['disabled'] = True
            event_form.fields['end_date'].widget.attrs['disabled'] = True
            event_form.fields['frequency'].widget.attrs['disabled'] = True

    return render(request, 'studentTSB/event_edit.html', context)


def event_occurrence_view(request, **kwargs):
    dm = DatabaseManager()
    states = dm.event_occurrence_states()
    event = dm.event_for_id(kwargs['id'])
    player_event_occurrences = dm.player_occurrences_for_event_and_date(kwargs['id'], kwargs['date'])
    players = [(p, SelectSingleForm('state', [(s.id, s.name) for s in states], initial={'state': p.state.id}))
               for p in player_event_occurrences]
    state_form = SelectSingleForm('state_all', [(s.id, s.name) for s in states])
    context = {'event': event, 'date': kwargs['date'], 'players': players, 'state_form': state_form}
    return render(request, 'studentTSB/event_occurrence.html', context)


def player_event_occurrence_from_player_view(request, **kwargs):
    if 'update-button' in request.POST:
        # this is an update
        DatabaseManager().update_player_event_occurrence(kwargs['id'], request.POST['rpe'],
                                                         request.POST['duration'],
                                                         request.POST['state_id'],
                                                         request.POST['comments'])
        return HttpResponseRedirect(f'/studentTSB/players/edit/{kwargs["player_id"]}/')

    else:
        occurrence = DatabaseManager().player_event_occurrence_for_id(kwargs['id'])
        context = {'player_event_occurrence': occurrence, 'player_id': kwargs['player_id'],
                   'form': PlayerEventOccurrenceForm(initial=occurrence.data_dictionary())}

        return render(request, 'studentTSB/player_event_occurrence.html', context)


def player_event_occurrence_from_event_view(request, **kwargs):
    if 'update-button' in request.POST:
        # this is an update
        DatabaseManager().update_player_event_occurrence(kwargs['id'], request.POST['rpe'],
                                                         request.POST['duration'],
                                                         request.POST['state_id'],
                                                         request.POST['comments'])
        return HttpResponseRedirect(f'/studentTSB/events/edit/{kwargs["event_id"]}/')

    else:
        occurrence = DatabaseManager().player_event_occurrence_for_id(kwargs['id'])
        context = {'player_event_occurrence': occurrence,
                   'form': PlayerEventOccurrenceForm(initial=occurrence.data_dictionary())}

        return render(request, 'studentTSB/player_event_occurrence.html', context)


def player_event_occurrence_from_event_occurrence_view(request, **kwargs):
    if 'update-button' in request.POST:
        # this is an update
        DatabaseManager().update_player_event_occurrence(kwargs['id'], request.POST['rpe'],
                                                         request.POST['duration'],
                                                         request.POST['state_id'],
                                                         request.POST['comments'])
        return HttpResponseRedirect(f'/studentTSB/events/occurrence/{kwargs["event_id"]}/{kwargs["date"]}/')

    else:
        occurrence = DatabaseManager().player_event_occurrence_for_id(kwargs['id'])
        context = {'player_event_occurrence': occurrence,
                   'form': PlayerEventOccurrenceForm(initial=occurrence.data_dictionary())}

        return render(request, 'studentTSB/player_event_occurrence.html', context)


def update_player_event_occurrence(request, **kwargs):
    dm = DatabaseManager()
    dm.update_player_event_occurrence(request.POST['id'], request.POST['rpe'], request.POST['duration'],
                                      request.POST['state'], request.POST['comments'])

    peo = dm.player_event_occurrence_for_id(request.POST['id'])
    messages.info(request, f'{peo} saved')

    return HttpResponseRedirect(f'/studentTSB/events/occurrence/edit/{kwargs["id"]}/{kwargs["date"]}/')


def update_all_player_event_duration(request, **kwargs):
    if request.POST['duration'] != 'hh:mm:ss':
        dm = DatabaseManager()
        occurrences = dm.player_occurrences_for_event_and_date(kwargs['id'], kwargs['date'])
        players_added = list()
        for o in occurrences:
            dm.update_player_event_occurrence(o.id, o.rpe, request.POST['duration'], o.state_id, o.comments)
            players_added.append(o.player.name)
        messages.info(request, f"duration updated to {request.POST['duration']} for {len(players_added)} players: {', '.join(players_added)}")
    return HttpResponseRedirect(f'/studentTSB/events/occurrence/edit/{kwargs["id"]}/{kwargs["date"]}/')


def update_all_player_event_rpe(request, **kwargs):
    dm = DatabaseManager()
    occurrences = dm.player_occurrences_for_event_and_date(kwargs['id'], kwargs['date'])
    players_added = list()
    for o in occurrences:
        dm.update_player_event_occurrence(o.id, request.POST['rpe'], o.duration, o.state_id, o.comments)
        players_added.append(o.player.name)
    messages.info(request, f"RPE updated to {request.POST['rpe']} for {len(players_added)} players: {', '.join(players_added)}")
    return HttpResponseRedirect(f'/studentTSB/events/occurrence/edit/{kwargs["id"]}/{kwargs["date"]}/')


def update_all_player_event_state(request, **kwargs):
    dm = DatabaseManager()
    occurrences = dm.player_occurrences_for_event_and_date(kwargs['id'], kwargs['date'])
    players_added = list()
    for o in occurrences:
        dm.update_player_event_occurrence(o.id, o.rpe, o.duration, request.POST['state_all'], o.comments)
        players_added.append(o.player.name)
    state = dm.event_occurrence_state_for_id(request.POST['state_all'])
    messages.info(request,
                  f"State updated to {state.name} for {len(players_added)} players: {', '.join(players_added)}")
    return HttpResponseRedirect(f'/studentTSB/events/occurrence/edit/{kwargs["id"]}/{kwargs["date"]}/')


def update_all_player_event_comments(request, **kwargs):
    dm = DatabaseManager()
    occurrences = dm.player_occurrences_for_event_and_date(kwargs['id'], kwargs['date'])
    players_added = list()
    for o in occurrences:
        dm.update_player_event_occurrence(o.id, o.rpe, o.duration, o.state_id, o.comments + ' ' + request.POST['comments'])
        players_added.append(o.player.name)
    messages.info(request,
                  f"Comments: {request.POST['comments']} added for {len(players_added)} players: {', '.join(players_added)}")
    return HttpResponseRedirect(f'/studentTSB/events/occurrence/edit/{kwargs["id"]}/{kwargs["date"]}/')


def event_generate_team_view(request, **kwargs):
    event = DatabaseManager().event_for_id(kwargs['id'])
    event.generate_team_occurrences()
    dd = {'id': kwargs['id']}
    return event_edit_view(request, **dd)


def event_generate_player_view(request, **kwargs):
    event = DatabaseManager().event_for_id(kwargs['id'])
    event.generate_player_occurrences()
    dd = {'id': kwargs['id']}
    return event_edit_view(request, **dd)


def event_save_view(request):
    dm = DatabaseManager()
    if 'id' in request.POST and request.POST['id'] != '':
        event_id = request.POST['id']
        event = dm.event_for_id(event_id)
        start_date = event.start_date if 'start_date' not in request.POST else request.POST['start_date']
        end_date = event.end_date if 'end_date' not in request.POST else request.POST['end_date']
        frequency = event.frequency if 'frequency' not in request.POST else request.POST['frequency']
        # existing event being edited
        dm.update_event(request.POST['id'], request.POST['name'], request.POST['start_time'], request.POST['end_time'],
                        request.POST['estimated_rpe'], start_date, end_date, frequency)
    else:
        # new event
        event_id = dm.add_new_event(request.POST['name'], request.POST['start_time'], request.POST['end_time'],
                                    request.POST['estimated_rpe'], request.POST['start_date'], request.POST['end_date'],
                                    request.POST['frequency'])
        # if team_id was passed in need to set this up as one of it's events
        if 'team_id' in request.POST and request.POST['team_id'] != '':
            print(request.POST)
            dm.add_team_to_event(request.POST['team_id'], event_id)

    # team = DatabaseManager().team_for_id(request.POST['team_id'])
    return HttpResponseRedirect(f'/studentTSB/events/edit/{event_id}/')


def player_edit_view(request, **kwargs):
    context = dict()
    if 'id' in kwargs:
        dm = DatabaseManager()
        player = dm.player_for_id(kwargs['id'])
        context['player'] = player
        initial_values = player.data_dictionary()
        context['player_name'] = player.name
        current_time = datetime.now().time().strftime("%H%M%S")
        file_name = f'player-{player.id}-TSB-{current_time}'
        tsb_for_player(player, file_name)
        context['graph_img'] = f'tmp/{file_name}.png'
        all_teams = dm.teams()
        team_id_dict = dict()
        for t in all_teams:
            team_id_dict[t.id] = t.name
        team_ids = set([t.id for t in all_teams]) - set([t.id for t in player.teams])
        team_choices = [(i, team_id_dict[i]) for i in team_ids]
        context['add_team_form'] = SelectForm('Teams', team_choices)
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


def player_personal_training_view(request, **kwargs):
    if request.method == "POST":
        # we're saving. This is personal training so is placed in personal team - this is team id 1 and the team even
        # with id 1
        dm = DatabaseManager()
        dm.add_new_player_event_occurrence(1, request.POST['player_id'], request.POST['date'], request.POST['rpe'],
                                           request.POST['duration'],request.POST['state_id'], request.POST['comments'])
        return HttpResponseRedirect(f'/studentTSB/players/edit/{request.POST["player_id"]}/')
    else:
        player = DatabaseManager().player_for_id(kwargs['player_id'])
        initial_values = {"player_id": player.id}
        return render(request, 'studentTSB/player_personal_training.html',
                      {'form': PersonalTrainingForm(initial=initial_values),
                       'player': player})


def add_teams_to_coach_view(request, **kwargs):
    dm = DatabaseManager()
    for tid in request.POST.getlist('Teams'):
        dm.add_coach_to_team(kwargs['id'], tid)

    return coach_edit_view(request, **kwargs)


def add_teams_to_player_view(request, **kwargs):
    dm = DatabaseManager()
    for tid in request.POST.getlist('Teams'):
        dm.add_player_to_team(kwargs['id'], tid)

    return player_edit_view(request, **kwargs)


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
        coach_teams = set()
        if coach.teams is not None:
            coach_teams = set([t.id for t in coach.teams])
        team_ids = set([t.id for t in all_teams]) - coach_teams
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
                      {'object': f"Player {player.name} from  {team.name}. NB this will also remove all future "
                                 f"PlayerEventOccurrences for this player and team"})
    if request.method == "POST":
        dm.remove_player_from_team(kwargs['player_id'], kwargs['team_id'])
        return HttpResponseRedirect(f'/studentTSB/teams/edit/{kwargs["team_id"]}/')


def remove_team_from_player(request, **kwargs):
    dm = DatabaseManager()
    if request.method == "GET":
        player = dm.player_for_id(kwargs['player_id'])
        team = dm.team_for_id(kwargs['team_id'])
        return render(request, 'studentTSB/confirm_delete.html',
                      {'object': f"Team {team.name} from  {player.name}. NB this will also remove all future "
                                 f"PlayerEventOccurrences for this player and team"})
    if request.method == "POST":
        dm.remove_player_from_team(kwargs['player_id'], kwargs['team_id'])
        return HttpResponseRedirect(f'/studentTSB/players/edit/{kwargs["player_id"]}/')


def delete_coach_from_team(request, **kwargs):
    dm = DatabaseManager()
    if request.method == "GET":
        coach = dm.coach_for_id(kwargs['coach_id'])
        team = dm.team_for_id(kwargs['team_id'])
        return render(request, 'studentTSB/confirm_delete.html',
                      {'object': f"Coach {coach.name} from  {team.name}"})
    if request.method == "POST":
        dm.remove_coach_from_team(kwargs['coach_id'], kwargs['team_id'])
        return HttpResponseRedirect(f'/studentTSB/teams/edit/{kwargs["team_id"]}/')


def delete_event(request, **kwargs):
    if request.method == "GET":
        event = DatabaseManager().event_for_id(kwargs['event_id'])
        return render(request, 'studentTSB/confirm_delete.html',
                      {'object': f"Event {event.name} for {event.teams_str}"})
    if request.method == "POST":
        DatabaseManager().delete_event(kwargs['event_id'])
        return HttpResponseRedirect(f'/studentTSB/events/list/')


def delete_event_from_team(request, **kwargs):
    dm = DatabaseManager()
    if request.method == "GET":
        event = dm.event_for_id(kwargs['event_id'])
        team = dm.team_for_id(kwargs['team_id'])
        team_occurrences = dm.team_event_occurrences(kwargs['event_id'], kwargs['team_id'])
        historic_occurrences = [o for o in team_occurrences if o.date < str(datetime.now().date())]
        message = f"""
            {team.name} from {event.name} and all associated training sessions. There have been 
            {len(historic_occurrences)} sessions prior to today which will be remoed. Are you sure ?
        """
        return render(request, 'studentTSB/confirm_delete.html',
                      {'object': message})
    if request.method == "POST":
        event = dm.event_for_id(kwargs['event_id'])
        team = dm.team_for_id(kwargs['team_id'])
        dm.remove_event_from_team(kwargs['event_id'], kwargs['team_id'])
        messages.info(request, f'{team.name} removed from {event.name} and all associated training sessions deleted')
        return HttpResponseRedirect(f'/studentTSB/teams/edit/{kwargs["team_id"]}')


def remove_team_from_event(request, **kwargs):
    r = delete_event_from_team(request, **kwargs)
    if request.method == 'POST':
        return HttpResponseRedirect(f'/studentTSB/events/edit/{kwargs["event_id"]}/')
    else:
        return r


def reading_type_edit(request, **kwargs):
    context = dict()
    if 'id' in kwargs:
        dm = DatabaseManager()
        reading_type = dm.reading_type_for_id(kwargs['id'])
        context['reading_type'] = reading_type
        initial_values = reading_type.data_dictionary()
    else:
        initial_values = dict()

    context['form'] = ReadingTypeEditForm(initial=initial_values)

    return render(request, 'studentTSB/reading_type_edit.html', context)


def reading_type_update(request):
    if 'id' in request.POST and request.POST['id'] != '':
        DatabaseManager().update_reading_type(request.POST['id'], request.POST['name'], request.POST['min_value'],
                                              request.POST['max_value'])
    else:
        DatabaseManager().add_new_reading_type(request.POST['name'], request.POST['min_value'], request.POST['max_value'])
    return reading_type_list_view(request)


def reading_edit(request, **kwargs):
    context = dict()
    if 'id' in kwargs:
        dm = DatabaseManager()
        reading = dm.reading_for_id(kwargs['id'])
        context['reading'] = reading
        context['event_occurrence'] = reading.player_event_occurrence
        initial_values = reading.data_dictionary()
    else:
        initial_values = {'player_event_occurrence_id': kwargs['player_event_occurrence_id']}
        context['player_event_occurrence'] = DatabaseManager().player_event_occurrence_for_id(kwargs['player_event_occurrence_id'])

    context['form'] = ReadingEditForm(initial=initial_values)

    return render(request, 'studentTSB/reading_edit.html', context)


def reading_update(request):
    if 'id' in request.POST and request.POST['id'] != '':
        reading_id = request.POST['id']
        DatabaseManager().update_reading(request.POST['id'], request.POST['value'], request.POST['name'],
                                         request.POST['player_event_occurrence_id'])
    else:
        reading_id = DatabaseManager().add_new_reading(request.POST['value'], request.POST['name'],
                                                       request.POST['player_event_occurrence_id'])
    reading = DatabaseManager().reading_for_id(reading_id)

    o_id = reading.player_event_occurrence.id
    player_id = reading.player_event_occurrence.player.id
    return HttpResponseRedirect(f'/studentTSB/players/event/occurrence/{o_id}/{player_id}/')


def delete_reading(request, **kwargs):
    dm = DatabaseManager()
    if request.method == "GET":
        reading = dm.reading_for_id(kwargs['id'])
        return render(request, 'studentTSB/confirm_delete.html',
                      {'object': f"Reading: {reading}"})
    if request.method == "POST":
        reading = dm.reading_for_id(kwargs['id'])
        o_id = reading.player_event_occurrence.id
        player_id = reading.player_event_occurrence.player.id
        dm.delete_reading(kwargs['id'])
        return HttpResponseRedirect(f'/studentTSB/players/event/occurrence/{o_id}/{player_id}/')
