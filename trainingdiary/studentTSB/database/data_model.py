import dateutil
import datetime


class Person:

    def __init__(self, *args):
        self.id = args[0]
        self.first_name = args[1]
        self.surname = args[2]
        self.known_as = args[3]
        self.email = args[4]
        self.name = f'{self.first_name} {self.surname}'

    def data_dictionary(self):
        return {'id': self.id,
                'first_name': self.first_name,
                'surname': self.surname,
                'known_as': self.known_as,
                'email': self.email}


class Player(Person):

    def __init__(self, *args):
        super().__init__(*args)
        self.dob = args[5]

    @property
    def teams(self):
        from . import DatabaseManager
        return DatabaseManager().teams_for_player(self.id)

    @property
    def team_count(self):
        return len(self.teams)

    @property
    def schedule(self):
        from . import DatabaseManager
        return DatabaseManager().event_occurrences_for_player(self.id)

    @property
    def tss_time_series(self):
        # the schedule may have two events in a day. Need to combine this schedule so only one item per date
        date_dict = dict()
        for s in self.schedule:
            d = dateutil.parser.parse(s.event_occurrence.date).date()
            date_dict[d] = date_dict.get(d, 0.0) + s.tss
        return date_dict.items()

    def data_dictionary(self):
        dd = super().data_dictionary()
        dd['dob'] = self.dob
        return dd


class Coach(Person):

    def __init__(self, *args):
        super().__init__(*args)

    @property
    def teams(self):
        from . import DatabaseManager
        return DatabaseManager().teams_for_coach(self.id)

    @property
    def team_count(self):
        return len(self.teams)

    @property
    def schedule(self):
        result = []
        for t in self.teams:
            result = result + t.schedule
        result.sort(key=lambda x: x.date)
        return result


class Event:

    def __init__(self, *args):
        self.id = args[0]
        self.name = args[1]
        self.start_time = args[2]
        self.end_time = args[3]
        self.estimated_rpe = args[4]
        self.start_date = args[5]
        self.end_date = args[6]
        self.frequency = args[7]
        self.duration = dateutil.parser.parse(self.end_time) - dateutil.parser.parse(self.start_time)

    @property
    def teams(self):
        from . import DatabaseManager
        return DatabaseManager().teams_for_event(self.id)

    @property
    def players(self):
        # unique list of players at event. If player in two teams for same event will only appear once
        player_ids = set()
        players = set()
        for t in self.teams:
            for p in t.players:
                if p.id not in player_ids:
                    players.add(p)
                    player_ids.add(p.id)
        return players

    @property
    def estimated_tss(self):
        return int((self.duration.seconds / 3600) * self.estimated_rpe * self.estimated_rpe * (100/49))

    @property
    def team_event_occurrences(self):
        from . import DatabaseManager
        return DatabaseManager().team_event_occurrences_for_event(self.id)

    @property
    def player_event_occurrences(self):
        from . import DatabaseManager
        return DatabaseManager().player_occurrences_for_event(self.id)

    @property
    def events_summary(self):
        occ_dict = dict()
        for o in self.team_event_occurrences:
            o_list = occ_dict.get(o.date, list())
            o_list.append(o)
            occ_dict[o.date] = o_list
        result = list()
        for k,v in occ_dict.items():
            result.append((k, ', '.join([t.team.name for t in v])))
        return result

    @property
    def number_of_occurrences(self):
        return len(self.team_event_occurrences)

    @property
    def tss_time_series(self):
        ts = []
        for e in self.team_event_occurrences:
            ts.append((dateutil.parser.parse(e.date).date(), self.estimated_tss))
        return ts

    def data_dictionary(self):
        return {'id': self.id,
                'name': self.name,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'estimated_rpe': self.estimated_rpe,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'frequency': self.frequency}

    @staticmethod
    def db_columns():
        return ['id', 'name', 'start_time', 'end_time', 'estimated_rpe', 'start_date', 'end_date', 'frequency']

    def generate_team_occurrences(self):
        from . import DatabaseManager
        dm = DatabaseManager()
        current_date = self.start_date
        if self.frequency == 'weekly':
            while current_date <= self.end_date:
                for t in self.teams:
                    # create team event occurrence
                    team_event_occurrence = dm.team_event_occurrence(self.id, t.id, current_date)
                    if team_event_occurrence is None:
                        dm.add_new_team_event_occurrence(self.id, t.id, current_date, self.estimated_tss, '')
                current_date = Event.__increment_by_one_week(current_date)
        else:
            for t in self.teams:
                team_event_occurrence = dm.team_event_occurrence(self.id, t.id, current_date)
                if team_event_occurrence is None:
                    dm.add_new_team_event_occurrence(self.id, t.id, current_date, self.estimated_tss, '')

    def generate_player_occurrences(self):
        from . import DatabaseManager
        dm = DatabaseManager()
        current_date = self.start_date
        if self.frequency == 'weekly':
            while current_date <= self.end_date:
                for p in self.players:
                    if not dm.player_event_occurrence_exists(self.id, p.id, current_date):
                        dm.add_new_player_event_occurrence(self.id, p.id, current_date, self.estimated_rpe,
                                                           self.duration, 1, '')
                current_date = Event.__increment_by_one_week(current_date)
        else:
            for p in self.players:
                if not dm.player_event_occurrence_exists(self.id, p.id, current_date):
                    dm.add_new_player_event_occurrence(self.id, p.id, current_date, self.estimated_rpe, self.duration,
                                                       1, '')

    @staticmethod
    def __increment_by_one_week(date_str):
        # works on date strings
        date = dateutil.parser.parse(date_str)
        date = date + datetime.timedelta(days=7)
        return str(date.date())


class TeamEventOccurrence:

    def __init__(self, *args):
        self.id = args[0]
        self.event_id = args[1]
        self.team_id = args[2]
        self.date = args[3]
        self.tss = args[4]
        self.comments = args[5]

    @property
    def team(self):
        from . import DatabaseManager
        return DatabaseManager().team_for_id(self.team_id)

    @property
    def event_date(self):
        return dateutil.parser.parse(self.date).date()

    @property
    def date_str(self):
        return dateutil.parser.parse(self.date).strftime('%a %d-%b-%y')

    @property
    def day(self):
        return dateutil.parser.parse(self.date).strftime('%A')

    @property
    def event(self):
        from . import DatabaseManager
        return DatabaseManager().event_for_id(self.event_id)

    @property
    def number_of_players(self):
        return len(self.team.players)


class PlayerEventOccurrence:

    def __init__(self, *args):
        self.id = args[0]
        self.event_id = args[1]
        self.player_id = args[2]
        self.date = args[3]
        self.rpe = args[4]
        self.duration = args[5]
        self.state_id = args[6]
        self.comments = args[7]

    @property
    def tss(self):
        if self.state.include_in_tsb:
            # the 100/49 factor is to make rpe = 7 threshold. ie 1hr @ rpe 7 == 100 TSS
            return int(self.hours * self.rpe * self.rpe * (100 / 49))
        else:
            return 0

    @property
    def state(self):
        from . import DatabaseManager
        return DatabaseManager().event_occurrence_state_for_id(self.state_id)

    @property
    def hours(self):
        time = dateutil.parser.parse(self.duration).time()
        # ignoring any milliseconds
        return time.hour + time.minute / 60.0 + time.second / 3600.0

    @property
    def day(self):
        return dateutil.parser.parse(self.date).strftime('%A')

    @property
    def estimated_tss(self):
        return self.event.estimated_tss

    @property
    def event(self):
        from . import DatabaseManager
        return DatabaseManager().event_for_id(self.event_id)

    @property
    def player(self):
        from . import DatabaseManager
        p = DatabaseManager().player_for_id(self.player_id)
        return p

    @property
    def teams_str(self):
        return ', '.join([t.name for t in self.teams])

    @property
    def teams(self):
        return [t for t in self.event.teams if t.player_in_team(self.player)]

    @property
    def readings(self):
        from . import DatabaseManager
        return DatabaseManager().readings_for_player(self.id)

    def data_dictionary(self):
        return {'id': self.id,
                'rpe': self.rpe,
                'duration': self.duration,
                'state_id': self.state_id,
                'comments': self.comments}


class Team:

    def __init__(self, *args):
        self.id = args[0]
        self.name = args[1]

    def player_in_team(self, player):
        return player.id in self.player_ids

    @property
    def events(self):
        from . import DatabaseManager
        return DatabaseManager().events_for_team(self.id)

    @property
    def number_of_events(self):
        return len(self.events)

    @property
    def player_ids(self):
        return set([p.id for p in self.players])

    @property
    def players(self):
        from . import DatabaseManager
        return DatabaseManager().players_for_team(self.id)

    @property
    def coaches(self):
        from . import DatabaseManager
        return DatabaseManager().coaches_for_team(self.id)

    @property
    def schedule(self):
        result = []
        for e in self.events:
            result = result + e.team_event_occurrences
        result.sort(key=lambda x: x.date)
        return result

    @property
    def tss_time_series(self):
        from . import combine_date_value_arrays
        return combine_date_value_arrays([ts.tss_time_series for ts in self.events])

    def __str__(self):
        return self.name

    def data_dictionary(self):
        return {'id': self.id,
                'name': self.name}


class ReadingType:

    def __init__(self, *args):
        self.id = args[0]
        self.name = args[1]
        self.min_value = args[2]
        self.max_value = args[3]

    def data_dictionary(self):
        return {'id': self.id,
                'name': self.name,
                'min_value': self.min_value,
                'max_value': self.max_value}


class Reading:

    def __init__(self, *args):
        self.id = args[0]
        self.value = args[1]
        self.type_id = args[2]
        self.player_event_occurrence_id = args[3]

    def __str__(self):
        return f'{self.reading_type.name}: {self.value} for {self.player_event_occurrence.player.name}'

    @property
    def reading_type(self):
        from . import DatabaseManager
        return DatabaseManager().reading_type_for_id(self.type_id)

    @property
    def player_event_occurrence(self):
        from . import DatabaseManager
        return DatabaseManager().player_event_occurrence_for_id(self.player_event_occurrence_id)

    def data_dictionary(self):
        return {'id': self.id,
                'value': self.value,
                'type_id': self.type_id,
                'player_event_occurrence_id': self.player_event_occurrence_id}


class EventOccurrenceState:

    def __init__(self, *args):
        self.id = args[0]
        self.name = args[1]
        self.include_in_tsb = args[2]

    @property
    def count(self):
        from . import DatabaseManager
        return DatabaseManager().number_of_occurrences_for_state_id(self.id)

    def __str__(self):
        return self.name
