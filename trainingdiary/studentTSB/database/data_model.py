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
        result = []
        for t in self.teams:
            result = result + t.schedule
        result.sort(key=lambda x: x.date)
        return result

    @property
    def tss_time_series(self):
        from . import combine_date_value_arrays
        return combine_date_value_arrays([ts.tss_time_series for ts in self.teams])


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
        self.team_id = args[8]

    @property
    def team(self):
        from . import DatabaseManager
        return DatabaseManager().team_for_id(self.team_id)

    @property
    def estimated_tss(self):
        return int((self.duration.seconds / 3600) * self.estimated_rpe * self.estimated_rpe * (100/49))

    @property
    def event_occurrences(self):
        from . import DatabaseManager
        return DatabaseManager().event_occurrences(self.id)

    @property
    def number_of_occurrences(self):
        return len(self.event_occurrences)

    @property
    def tss_time_series(self):
        ts = []
        for e in self.event_occurrences:
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
                'frequency': self.frequency,
                'team_id': self.team_id}

    @staticmethod
    def db_columns():
        return ['id', 'name', 'start_time', 'end_time', 'estimated_rpe', 'start_date', 'end_date', 'frequency',
                'team_id']

    def generate_occurrences(self):
        from . import DatabaseManager
        dm = DatabaseManager()
        current_date = self.start_date
        if self.frequency == 'weekly':
            while current_date <= self.end_date:
                if not dm.event_occurrence_exists(self.id, current_date):
                    dm.add_new_event_occurrency(self.id, current_date, self.estimated_tss)
                current_date = Event.__increment_by_one_week(current_date)
        else:
            if not dm.event_occurrence_exists(self.id, current_date):
                dm.add_new_event_occurrency(self.id, current_date, self.estimated_tss)

    @staticmethod
    def __increment_by_one_week(date_str):
        # works on date strings
        date = dateutil.parser.parse(date_str)
        date = date + datetime.timedelta(days=7)
        return str(date.date())


class EventOccurrence:

    def __init__(self, *args):
        self.id = args[0]
        self.event_id = args[1]
        self.date = args[2]
        self.tss = args[3]

    @property
    def day(self):
        return dateutil.parser.parse(self.date).strftime('%A')

    @property
    def event(self):
        from . import DatabaseManager
        return DatabaseManager().event_for_id(self.event_id)


class Team:

    def __init__(self, *args):
        self.id = args[0]
        self.name = args[1]

    @property
    def events(self):
        from . import DatabaseManager
        return DatabaseManager().events_for_team(self.id)

    @property
    def number_of_events(self):
        return len(self.events)

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
            result = result + e.event_occurrences
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