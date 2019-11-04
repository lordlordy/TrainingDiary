import sqlite3
import os
import trainingdiary
import datetime

SCHEDULED_STATE = 'Scheduled'
COMPLETED_STATE = 'Completed'
occurrence_states = [[SCHEDULED_STATE, 1], [COMPLETED_STATE, 1], ['Authorised Absent', 0], ['Absent', 0]]

db_tables_sql = [
    f'''
         CREATE TABLE Person(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         first_name varchar(32) NOT NULL,
         surname varchar(32) NOT NULL,
         known_as varchar(32) NOT NULL,
         email varchar(256) NOT NULL UNIQUE
         );
    ''',
    f'''
         CREATE TABLE Player(
         id INTEGER PRIMARY KEY REFERENCES Person(id),
         date_of_birth Date NOT NULL
         );
    ''',
    f'''
         CREATE TABLE Coach(
         id INTEGER PRIMARY KEY REFERENCES Person(id)
         );
    ''',
    f'''
         CREATE TABLE Team(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name varchar(64) NOT NULL
         );
    ''',
    f'''
         CREATE TABLE TeamPlayer(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             team_id INTEGER REFERENCES Team(id),
             player_id INTEGER REFERENCES Player(id),
             UNIQUE(team_id, player_id)
         );
    ''',
    f'''
         CREATE TABLE TeamCoach(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             team_id INTEGER REFERENCES Team(id),
             coach_id INTEGER REFERENCES Coach(id),
             UNIQUE(team_id, coach_id)
         );
    ''',
    f'''
         CREATE TABLE Event(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name varchar(64) NOT NULL,
             start_time Time NOT NULL,
             end_time Time NOT NULL,
             estimated_rpe REAL NOT NULL,
             start_date Date NOT NULL,
             end_date Date NOT NULL,
             frequency varchar(16) NOT NULL
         );
    ''',
    f'''
         CREATE TABLE TeamEvent(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER REFERENCES Team(id),
            event_id INTEGER REFERENCES Event(id),
            UNIQUE(team_id, event_id)
        );
    ''',
    f'''
         CREATE TABLE TeamEventOccurrence(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             event_id INTEGER NOT NULL REFERENCES Event(id),
             team_id INTEGER NOT NULL REFERENCES Team(id),
             date Date NOT NULL,
             tss REAL NOT NULL,
             comments TEXT
         );
    ''',
    f'''
         CREATE TABLE PlayerEventOccurrence(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             event_id INTEGER NOT NULL REFERENCES Event(id),
             player_id INTEGER NOT NULL REFERENCES Event(id),
             date Date NOT NULL,
             rpe REAL NOT NULL,
             duration REAL NOT NULL,
             state_id INTEGER REFERENCES EventOccurrenceState(id),
             comments TEXT,
             UNIQUE(event_id, player_id, date)
         );
    ''',
    f'''
        CREATE TABLE ReadingType(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name varchar(32) NOT NULL,
            min_value REAL NOT NULL,
            max_value REAL NOT NULL
        );
    ''',
    f'''
        CREATE TABLE Reading(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value REAL NOT NULL,
            type_id INTEGER NOT NULL REFERENCES ReadingType(id),
            player_event_occurrence_id INTEGER NOT NULL REFERENCES PlayerEventOccurrence(id)
        );
    ''',
    f'''
        CREATE TABLE EventOccurrenceState(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name varchar(32) NOT NULL,
            include_in_tsb BOOL NOT NULL 
        );
    '''
]


class DatabaseManager:
    DB_NAME = 'TeamTraining.sqlite3'

    def __init__(self):
        db_path = os.path.join(trainingdiary.BASE_DIR, DatabaseManager.DB_NAME)
        self.__conn = sqlite3.connect(db_path)

    def create_db(self):
        for sql in db_tables_sql:
            try:
                self.__conn.execute(sql)
                self.__conn.commit()
            except Exception as e:
                print(e)
                print(sql)
        # create Personal Training event
        self.add_new_event('Personal Training', '00:00:00', '01:00:00', 5.0, '2019-01-01', '2099-12-31', 'Adhoc')
        self.create_happiness_reading()
        for s in occurrence_states:
            self.add_event_occurrence_state(s[0], s[1])

    def create_dummy_data(self):
        for p in dummy_players:
            self.add_new_player(p[0], p[1], p[2], p[3], p[4])
        for c in dummy_coaches:
            self.add_new_coach(c[0], c[1], c[2], c[3])
        for t in dummy_teams:
            self.add_new_team(t[0])
        for p in dummy_team_player:
            self.__add_new_team_player(p[0], p[1])
        for c in dummy_team_coach:
            self.__add_new_team_coach(c[0], c[1])
        for e in dummy_events:
            id = self.add_new_event(e[0], e[1], e[2], e[3], e[4], e[5], e[6])
        for te in dummy_team_events:
            self.__add_new_team_event(te[0],te[1])

    def create_happiness_reading(self):
        self.add_new_reading_type('happiness', 0, 3)

    def state_id_for_name(self, name):
        sql = f'''
            SELECT id FROM EventOccurrenceState WHERE name='{name}'
        '''
        ids = self.__conn.execute(sql).fetchall()
        if len(ids) > 0:
            return ids[0][0]

    def update_player_event_occurrence_state(self):
        # This looks for all player event occurrences that are today or before that are state == 'scheduled'
        # all these are changed to 'completed'
        completed_id = self.state_id_for_name(COMPLETED_STATE)
        scheduled_id = self.state_id_for_name(SCHEDULED_STATE)
        if completed_id is not None and scheduled_id is not None:
            today = datetime.datetime.now().date()
            sql = f'''
                UPDATE PlayerEventOccurrence
                SET state_id='{completed_id}'
                WHERE state_id='{scheduled_id}' AND date <= '{today}'
            '''
            self.__conn.execute(sql)
            self.__conn.commit()

    def players(self):
        sql = f'''
            SELECT Player.id, Person.first_name, Person.surname, Person.known_as, Person.email, Player.date_of_birth
            FROM Player, Person
            WHERE Player.id=Person.id 
        '''
        return self.__players_from_sql(sql)

    def player_for_id(self, player_id):
        sql = f'''
                    SELECT Player.id, Person.first_name, Person.surname, Person.known_as, Person.email, Player.date_of_birth
                    FROM Player, Person
                    WHERE Player.id=Person.id  AND Player.id={player_id}
                '''
        players = self.__players_from_sql(sql)
        if len(players) > 0:
            return players[0]

    def coaches(self):
        sql = f'''
            SELECT Coach.id, Person.first_name, Person.surname, Person.known_as, Person.email
            FROM Coach, Person
            WHERE Coach.id=Person.id 
        '''
        return self.__coaches_from_sql(sql)

    def coach_for_id(self, coach_id):
        sql = f'''
            SELECT Coach.id, Person.first_name, Person.surname, Person.known_as, Person.email
            FROM Coach, Person
            WHERE Coach.id=Person.id AND Coach.id={coach_id}
        '''
        coaches = self.__coaches_from_sql(sql)
        if len(coaches) > 0:
            return coaches[0]

    def teams(self):
        sql = f'''
            SELECT id, name
            FROM Team
        '''
        return self.__teams_from_sql(sql)

    def team_for_id(self, team_id):
        sql = f'''
            SELECT id, name
            FROM Team
            WHERE id={team_id}
        '''
        teams = self.__teams_from_sql(sql)
        if len(teams) > 0:
            return teams[0]

    def teams_for_player(self, player_id):
        sql = f'''
            SELECT DISTINCT(team_id) FROM TeamPlayer WHERE player_id={player_id}
        '''
        team_ids = self.__conn.execute(sql).fetchall()
        teams = [self.team_for_id(tid[0]) for tid in team_ids]
        return teams

    def teams_for_coach(self, coach_id):
        sql = f'''
            SELECT DISTINCT(team_id) FROM TeamCoach WHERE coach_id={coach_id}
        '''
        team_ids = self.__conn.execute(sql).fetchall()
        teams = [self.team_for_id(tid[0]) for tid in team_ids]
        return teams

    def teams_for_event(self, event_id):
        sql = f'''
            SELECT DISTINCT(team_id) FROM TeamEvent WHERE event_id={event_id}
        '''
        team_ids = self.__conn.execute(sql).fetchall()
        teams = [self.team_for_id(tid[0]) for tid in team_ids]
        return teams

    def events_for_team(self, team_id):
        sql = f'''
            SELECT DISTINCT(event_id) FROM TeamEvent WHERE team_id={team_id}
        '''
        event_ids = self.__conn.execute(sql).fetchall()
        events = [self.event_for_id(eid[0]) for eid in event_ids]
        return events

    def event_for_id(self, event_id):
        from . import Event
        sql = f'''
            SELECT {','.join(Event.db_columns())}
            FROM Event
            WHERE id={event_id}
        '''
        events = self.__events_for_sql(sql)
        if len(events) > 0:
            return events[0]

    def update_event(self, event_id, name, start_time, end_time, estimated_rpe, start_date, end_date, frequency):
        sql = f'''
            UPDATE Event
            SET
            name='{name}', start_time='{start_time}', end_time='{end_time}', estimated_rpe={estimated_rpe}, 
            start_date='{start_date}', end_date='{end_date}', frequency='{frequency}'
            WHERE id={event_id}
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def events(self):
        from . import Event
        sql = f'''
            SELECT {','.join(Event.db_columns())}
            FROM Event
        '''
        return self.__events_for_sql(sql)

    def team_event_occurrences_for_event(self, event_id):
        sql = f'''
            SELECT id, event_id, team_id, date, tss, comments
            FROM TeamEventOccurrence
            WHERE event_id={event_id}
        '''
        return self.__event_occurrences_for_sql(sql)

    def team_event_occurrences(self, event_id, team_id):
        sql = f'''
            SELECT id, event_id, team_id, date, tss, comments
            FROM TeamEventOccurrence
            WHERE event_id={event_id} AND team_id={team_id}
        '''
        return self.__event_occurrences_for_sql(sql)

    def team_event_occurrence_for_id(self, team_event_occurrence_id):

        sql = f'''
            SELECT id, event_id, team_id, date, tss, comments
            FROM TeamEventOccurrence
            WHERE id={team_event_occurrence_id}
        '''
        occurrences = self.__event_occurrences_for_sql(sql)
        if len(occurrences) > 0:
            return occurrences[0]
        else:
            return []

    def team_event_occurrence(self, event_id, team_id, date):
        sql = f'''
            SELECT id, event_id, team_id, date, tss, comments
            FROM TeamEventOccurrence
            WHERE event_id={event_id} AND team_id={team_id} AND date='{date}'
        '''
        occurrences = self.__event_occurrences_for_sql(sql)
        if len(occurrences) > 0:
            return occurrences[0]
        else:
            return None

    def event_occurrences_for_player(self, player_id):

        sql = f'''
            SELECT id, event_id, player_id, date, rpe, duration, state_id, comments
            FROM PlayerEventOccurrence
            WHERE player_id={player_id}
        '''
        return self.__player_event_occurrences_for_sql(sql)

    def player_occurrences_for_event(self, event_id):
        sql = f'''
            SELECT id, event_id, player_id, date, rpe, duration, state_id, comments
            FROM PlayerEventOccurrence
            WHERE event_id={event_id}
        '''
        return self.__player_event_occurrences_for_sql(sql)

    def player_occurrences_for_event_and_date(self, event_id, date):
        sql = f'''
            SELECT id, event_id, player_id, date, rpe, duration, state_id, comments
            FROM PlayerEventOccurrence
            WHERE event_id={event_id} and date='{date}'
        '''
        return self.__player_event_occurrences_for_sql(sql)

    def player_event_occurrence_for_id(self, player_event_occurrence_id):
        sql = f'''
            SELECT id, event_id, player_id, date, rpe, duration, state_id, comments
            FROM PlayerEventOccurrence
            WHERE id={player_event_occurrence_id}
        '''
        occurrences = self.__player_event_occurrences_for_sql(sql)
        if len(occurrences) > 0:
            return occurrences[0]

    def team_event_occurrence_exists(self, event_id, team_id, date):
        sql = f'''
            SELECT id FROM TeamEventOccurrence
            WHERE event_id={event_id} AND team_id={team_id} AND date='{date}'
        '''
        occurrences = self.__conn.execute(sql).fetchall()
        return len(occurrences) > 0

    def player_event_occurrence_exists(self, event_id, player_id, date):
        sql = f'''
            SELECT id FROM PlayerEventOccurrence
            WHERE event_id={event_id} AND player_id='{player_id}' AND date='{date}'
        '''
        occurrences = self.__conn.execute(sql).fetchall()
        return len(occurrences) > 0

    def update_player_event_occurrence(self, player_event_occurrence_id, rpe, duration, state_id, comments):
        sql = f'''
            UPDATE PlayerEventOccurrence
            SET rpe={rpe}, duration='{duration}', state_id='{state_id}', comments='{comments}'
            WHERE id={player_event_occurrence_id}
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def update_player(self, player_id, first_name, surname, known_as, email, dob):
        self.__update_person(player_id, first_name, surname, known_as, email)
        sql = f'''
            UPDATE Player SET date_of_birth='{dob}' WHERE id={player_id}
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def add_new_player(self, first_name, surname, known_as, email, dob):
        last_id = self.__add_new_person(first_name, surname, known_as, email)
        player_sql = f'''
            INSERT INTO Player
            (id, date_of_birth)
            VALUES
            ({last_id}, '{dob}')
        '''
        self.__conn.execute(player_sql)
        self.__conn.commit()

    def add_player_to_team(self, player_id, team_id):
        self.__add_new_team_player(team_id, player_id)

    def add_team_to_event(self, team_id, event_id):
        self.__add_new_team_event(team_id, event_id)

    def remove_player_from_team(self, player_id, team_id):
        sql = f'''
            DELETE FROM TeamPlayer
            WHERE player_id={player_id} AND team_id={team_id}
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def add_coach_to_team(self, coach_id, team_id):
        self.__add_new_team_coach(team_id, coach_id)

    def remove_coach_from_team(self, coach_id, team_id):
        sql = f'''
            DELETE FROM TeamCoach
            WHERE coach_id={coach_id} AND team_id={team_id}
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def update_coach(self, coach_id, first_name, surname, known_as, email):
        self.__update_person(coach_id, first_name, surname, known_as, email)

    def add_new_coach(self, first_name, surname, known_as, email):
        coach_id = self.__add_new_person(first_name, surname, known_as, email)
        coach_sql = f'''
            INSERT INTO Coach
            (id) VALUES ({coach_id})
        '''
        self.__conn.execute(coach_sql)
        self.__conn.commit()

    def update_team(self, team_id, team_name):
        sql = f'''
            UPDATE Team
            SET name='{team_name}'
            WHERE id={team_id}
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def add_new_team(self, team_name):
        team_sql = f'''
            INSERT INTO Team
            (name)
            VALUES
            ('{team_name}')
        '''
        self.__conn.execute(team_sql)
        self.__conn.commit()

    def add_new_event(self, event_name, start_time, end_time, estimated_rpe, start_date, end_date, frequency):
        sql = f'''
            INSERT INTO Event
            (name, start_time, end_time, estimated_rpe, start_date, end_date, frequency)
            VALUES
            ('{event_name}', '{start_time}', '{end_time}', {estimated_rpe}, '{start_date}', '{end_date}', '{frequency}')
         ;
        '''
        self.__conn.execute(sql)
        self.__conn.commit()
        last_id = self.__conn.execute('SELECT last_insert_rowid()').fetchall()[0][0]
        return last_id

    def add_new_team_event_occurrence(self, event_id, team_id, date, tss, comments):
        sql = f'''
            INSERT INTO TeamEventOccurrence
            (event_id, team_id, date, tss, comments)
            VALUES
            ({event_id}, {team_id}, '{date}', {tss}, '{comments}')
        '''
        self.__conn.execute(sql)
        self.__conn.commit()
        last_id = self.__conn.execute('SELECT last_insert_rowid()').fetchall()[0][0]
        return last_id

    def add_new_player_event_occurrence(self, event_id, player_id, date, rpe, duration, state_id, comments):
        sql = f'''
            INSERT INTO PlayerEventOccurrence
            (event_id, player_id, date, rpe, duration, state_id, comments)
            VALUES
            ({event_id}, {player_id}, '{date}', {rpe}, '{duration}', '{state_id}', '{comments}')
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def players_for_team(self, team_id):
        sql = f'''
            SELECT Player.id, Person.first_name, Person.surname, Person.known_as, Person.email, Player.date_of_birth
            FROM Player, Person, TeamPlayer
            WHERE Player.id=Person.id AND Player.id=TeamPlayer.player_id AND TeamPlayer.team_id={team_id}
        '''
        return self.__players_from_sql(sql)

    def coaches_for_team(self, team_id):
        sql = f'''
            SELECT Coach.id, Person.first_name, Person.surname, Person.known_as, Person.email
            FROM Coach, Person, TeamCoach
            WHERE Coach.id=Person.id AND Coach.id=TeamCoach.coach_id AND TeamCoach.team_id={team_id}
        '''
        coaches = self.__coaches_from_sql(sql)
        return coaches

    def remove_event_from_team(self, event_id, team_id):
        # delete team event occurrences first
        sql = f'DELETE FROM TeamEventOccurrence WHERE event_id={event_id} AND team_id={team_id}'
        self.__conn.execute(sql)
        self.__conn.commit()
        # Finally remove TeamEvent
        sql = f'DELETE FROM TeamEvent WHERE event_id={event_id} AND team_id={team_id}'
        self.__conn.execute(sql)
        self.__conn.commit()
        # need to check players for this event and remove their occurrences if there is no longer a team they're
        # in associated with this event
        event = self.event_for_id(event_id)
        for p in event.player_event_occurrences:
            if len(p.teams) == 0:
                sql = f'DELETE FROM PlayerEventOccurrence WHERE id={p.id}'
                self.__conn.execute(sql)
                self.__conn.commit()

    def number_of_occurrences_for_state_id(self, state_id):
        sql = f'''
            SELECT count(id) FROM PlayerEventOccurrence WHERE state_id={state_id}
        '''
        count = self.__conn.execute(sql).fetchall()
        return count[0][0]

    def event_occurrence_states(self):
        sql = f'''
            SELECT id, name, include_in_tsb FROM EventOccurrenceState
        '''
        return self.__event_occurrence_states_from_sql(sql)

    def add_event_occurrence_state(self, name, include_in_tsb):
        sql = f'''
            INSERT INTO EventOccurrenceState
            (name, include_in_tsb)
            VALUES
            ('{name}', {include_in_tsb})
        '''
        self.__conn.execute(sql)
        self.__conn.commit()
        status_id = self.__conn.execute('SELECT last_insert_rowid()').fetchall()[0][0]
        return status_id

    def update_event_occurrence_state(self, state_id, name, include_in_tsb=1):
        sql = f'''
            UPDATE EventOccurrenceState
            SET
            name='{name}', include_in_tsb='{include_in_tsb}'
            WHERE id={state_id}
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def event_occurrence_state_for_id(self, state_id):
        sql = f'''
            SELECT id, name, include_in_tsb FROM EventOccurrenceState
            WHERE id={state_id}
        '''
        states = self.__event_occurrence_states_from_sql(sql)
        if len(states) > 0:
            return states[0]

    def delete_event(self, event_id):
        # for now only delete if there are no occurrences
        players = self.__conn.execute(f'SELECT COUNT(id) FROM PlayerEventOccurrence WHERE event_id={event_id}').fetchall()
        teams = self.__conn.execute(f'SELECT COUNT(id) FROM TeamEventOccurrence WHERE event_id={event_id}').fetchall()

        if len(players) > 0 and len(teams) > 0 and players[0][0] == 0 and teams[0][0] == 0:
            self.__conn.execute(f'DELETE From Event WHERE id={event_id}')
            self.__conn.commit()

    def delete_event_occurrence_state(self, state_id):
        sql = f'DELETE FROM EventOccurrenceState WHERE id={state_id}'
        self.__conn.execute(sql)
        self.__conn.commit()

    def add_new_reading_type(self, name, min_value, max_value):
        sql = f'''
            INSERT INTO ReadingType
            (name, min_value, max_value)
            VALUES
            ('{name}', {min_value}, {max_value})
        '''
        self.__conn.execute(sql)
        self.__conn.commit()
        type_id = self.__conn.execute('SELECT last_insert_rowid()').fetchall()[0][0]
        return type_id

    def update_reading_type(self, type_id, name, min_value, max_value):
        sql = f'''
            UPDATE ReadingType
            SET
            name='{name}', min_value={min_value}, max_value={max_value}
            WHERE id={type_id}
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def reading_types(self):
        sql = f'''
            SELECT id, name, min_value, max_value FROM ReadingType
        '''
        return self.__reading_types_from_sql(sql)

    def reading_type_for_id(self, reading_type_id):
        sql = f'''
            SELECT id, name, min_value, max_value FROM ReadingType WHERE id={reading_type_id}
        '''
        types = self.__reading_types_from_sql(sql)
        if len(types) > 0:
            return types[0]

    def add_new_reading(self, value, type_id, player_event_occurrence_id):
        sql = f'''
            INSERT INTO Reading
            (value, type_id, player_event_occurrence_id)
            VALUES
            ({value}, {type_id}, {player_event_occurrence_id})
        '''
        self.__conn.execute(sql)
        self.__conn.commit()
        reading_id = self.__conn.execute('SELECT last_insert_rowid()').fetchall()[0][0]
        return reading_id

    def update_reading(self, reading_id, value, type_id, player_event_occurrence_id):
        sql = f'''
            UPDATE Reading
            SET
            value={value}, type_id={type_id}, player_event_occurrence_id={player_event_occurrence_id}
            WHERE id={reading_id}
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def delete_reading(self, reading_id):
        sql = f'''DELETE FROM Reading where id={reading_id}'''
        self.__conn.execute(sql)
        self.__conn.commit()

    def readings_for_player(self, player_event_occurrence_id):
        sql = f'''
            SELECT id, value, type_id, player_event_occurrence_id FROM Reading 
            WHERE player_event_occurrence_id={player_event_occurrence_id}
        '''
        return self.__readings_from_sql(sql)

    def reading_for_id(self, reading_id):
        sql = f'''
            SELECT id, value, type_id, player_event_occurrence_id FROM READING WHERE id={reading_id}
        '''
        reading = self.__readings_from_sql(sql)
        if len(reading) > 0:
            return reading[0]

    def __add_new_team_player(self, team_id, player_id):
        sql = f'''
            INSERT INTO TeamPlayer
            (team_id, player_id)
            VALUES
            ({team_id}, {player_id})
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def __add_new_team_event(self, team_id, event_id):
        sql = f'''
            INSERT INTO TeamEvent
            (team_id, event_id)
            VALUES
            ({team_id}, {event_id})
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def __add_new_team_coach(self, team_id, coach_id):
        sql = f'''
            INSERT INTO TeamCoach
            (team_id, coach_id)
            VALUES
            ({team_id}, {coach_id})
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def __update_person(self, person_id, first_name, surname, known_as, email):
        sql = f'''
            UPDATE Person
            SET
            first_name='{first_name}', surname='{surname}', known_as='{known_as}', email='{email}'
            WHERE id={person_id}
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def __add_new_person(self, first_name, surname, known_as, email):
        person_sql = f'''
            INSERT INTO Person
            (first_name, surname, known_as, email)
            VALUES
            ('{first_name}', '{surname}', '{known_as}', '{email}')
        '''
        self.__conn.execute(person_sql)
        self.__conn.commit()
        last_id = self.__conn.execute('SELECT last_insert_rowid()').fetchall()[0][0]
        return last_id

    def __event_occurrence_states_from_sql(self, sql):
        states = self.__conn.execute(sql).fetchall()
        from . import EventOccurrenceState
        return [EventOccurrenceState(*s) for s in states]

    def __readings_from_sql(self, sql):
        readings = self.__conn.execute(sql).fetchall()
        from . import Reading
        return [Reading(*r) for r in readings]

    def __reading_types_from_sql(self, sql):
        types = self.__conn.execute(sql).fetchall()
        from . import ReadingType
        return [ReadingType(*t) for t in types]

    def __players_from_sql(self, sql):
        players = self.__conn.execute(sql).fetchall()
        from . import Player
        return [Player(*p) for p in players]

    def __teams_from_sql(self, sql):
        teams = self.__conn.execute(sql).fetchall()
        from . import Team
        return [Team(*t) for t in teams]

    def __coaches_from_sql(self, sql):
        coaches = self.__conn.execute(sql).fetchall()
        from . import Coach
        return [Coach(*c) for c in coaches]

    def __events_for_sql(self, sql):
        events = self.__conn.execute(sql).fetchall()
        from . import Event
        return [Event(*e) for e in events]

    def __event_occurrences_for_sql(self, sql):
        events = self.__conn.execute(sql).fetchall()
        from . import TeamEventOccurrence
        return [TeamEventOccurrence(*e) for e in events]

    def __player_event_occurrences_for_sql(self, sql):
        player_events = self.__conn.execute(sql).fetchall()
        from . import PlayerEventOccurrence
        return [PlayerEventOccurrence(*e) for e in player_events]



dummy_players = [
    ['Player', 'One', '1', '1@email.com', '2002-04-05'],
    ['Player', 'Two', '2', '2@email.com', '2002-04-05'],
    ['Player', 'Three', '3', '3@email.com', '2002-04-05'],
    ['Player', 'Four', '4', '4@email.com', '2002-04-05'],
    ['Player', 'Five', '5', '5@email.com', '2002-04-05'],
    ['Player', 'Six', '6', '6@email.com', '2002-04-05'],
    ['Player', 'Seven', '7', '7@email.com', '2002-04-05'],
    ['Player', 'Eight', '8', '8@email.com', '2002-04-05'],
    ['Player', 'Nine', '9', '9@email.com', '2002-04-05'],
    ['Player', 'Ten', '10', '10@email.com', '2002-04-05'],
    ['Player', 'Eleven', '11', '11@email.com', '2002-04-05'],
]

dummy_coaches = [
    ['Coach', 'One', 'C1', 'c1@email.com'],
    ['Coach', 'Two', 'C2', 'c2@email.com'],
    ['Coach', 'Three', 'C3', 'c3@email.com'],
    ['Coach', 'Four', 'C4', 'c4@email.com'],
]

dummy_teams = [
    ['Rugby A'],
    ['Cricket A'],
    ['Rugby B'],
    ['Swim Squad']
]

dummy_team_coach = [
    [2, 12],
    [2, 13],
    [2, 14],
    [3, 15],
    [4, 14],
    [5, 12],
    [6, 12]
]

dummy_team_player = [
    [1, 1],
    [1, 2],
    [1, 3],
    [1, 4],
    [1, 5],
    [2, 1],
    [2, 4],
    [2, 6],
    [2, 8],
    [3, 7],
    [3, 9],
    [3, 10],
    [3, 11],
    [4, 5],
]

dummy_events = [
    ['Main Practice', '17:00:00', '19:00:00', 5.0, '2019-09-30', '2020-03-15', 'weekly'],
    ['2nd Practice', '17:00:00', '19:00:00', 5.1, '2019-10-02', '2020-03-15', 'weekly'],
    ['Match - St Pauls', '09:00:00', '10:30:00', 6.0, '2019-10-05', '2019-10-05', 'one off'],
    ['Match - Eton', '09:00:00', '10:30:00', 6.0, '2019-10-12', '2019-10-12', 'one off'],
    ['Match - Old Boys', '09:00:00', '10:30:00', 5.5, '2019-10-19', '2019-10-19', 'one off'],
    ['Main Practice', '17:00:00', '19:00:00', 5.6, '2019-09-30', '2020-03-15', 'weekly'],
    ['2nd Practice', '17:00:00', '19:00:00', 4.8, '2019-10-01', '2020-03-15', 'weekly'],
    ['Main Practice', '17:00:00', '19:00:00', 6.0, '2019-10-02', '2020-03-15', 'weekly'],
    ['2nd Practice', '17:00:00', '19:00:00', 5.6, '2019-10-04', '2020-03-15', 'weekly'],
    ['Mon Training', '17:00:00', '18:00:00', 5.2, '2019-09-30', '2020-03-15', 'weekly'],
    ['Tue Training', '17:00:00', '18:00:00', 5.9, '2019-10-01', '2020-03-15', 'weekly'],
    ['Wed Training', '17:00:00', '18:00:00', 4.5, '2019-10-02', '2020-03-15', 'weekly'],
    ['Thu Training', '17:00:00', '18:00:00', 5.1, '2019-10-03', '2020-03-15', 'weekly'],
    ['Fri Training', '17:00:00', '18:00:00', 5.7, '2019-10-04', '2020-03-15', 'weekly'],
]

dummy_team_events = [
    [1, 2],
    [1, 3],
    [1, 4],
    [1, 5],
    [1, 6],
    [2, 7],
    [2, 8],
    [3, 9],
    [3, 10],
    [3, 4],
    [3, 5],
    [3, 6],
    [4, 11],
    [4, 12],
    [4, 13],
    [4, 14],
    [4, 15],
]


if __name__ == '__main__':
    print('Running')
    DatabaseManager().create_db()