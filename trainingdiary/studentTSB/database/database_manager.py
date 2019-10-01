import sqlite3
import os
import trainingdiary


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
    [1, 12],
    [1, 13],
    [1, 14],
    [2, 15],
    [3, 14],
    [3, 12],
    [4, 12]
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
    ['Main Practice', '17:00:00', '19:00:00', 5.0, '2019-09-30', '2020-03-15', 'weekly', 1],
    ['2nd Practice', '17:00:00', '19:00:00', 5.1, '2019-10-02', '2020-03-15', 'weekly', 1],
    ['Match - St Pauls', '09:00:00', '10:30:00', 6.0, '2019-10-05', '2019-10-05', 'one off', 1],
    ['Match - Eton', '09:00:00', '10:30:00', 6.0, '2019-10-12', '2019-10-12', 'one off', 1],
    ['Match - Old Boys', '09:00:00', '10:30:00', 5.5, '2019-10-19', '2019-10-19', 'one off', 1],
    ['Main Practice', '17:00:00', '19:00:00', 5.6, '2019-09-30', '2020-03-15', 'weekly', 2],
    ['2nd Practice', '17:00:00', '19:00:00', 4.8, '2019-10-01', '2020-03-15', 'weekly', 2],
    ['Main Practice', '17:00:00', '19:00:00', 6.0, '2019-10-02', '2020-03-15', 'weekly', 3],
    ['2nd Practice', '17:00:00', '19:00:00', 5.6, '2019-10-04', '2020-03-15', 'weekly', 3],
    ['Mon Training', '17:00:00', '18:00:00', 5.2, '2019-09-30', '2020-03-15', 'weekly', 4],
    ['Tue Training', '17:00:00', '18:00:00', 5.9, '2019-10-01', '2020-03-15', 'weekly', 4],
    ['Wed Training', '17:00:00', '18:00:00', 4.5, '2019-10-02', '2020-03-15', 'weekly', 4],
    ['Thu Training', '17:00:00', '18:00:00', 5.1, '2019-10-03', '2020-03-15', 'weekly', 4],
    ['Fri Training', '17:00:00', '18:00:00', 5.7, '2019-10-04', '2020-03-15', 'weekly', 4],
]

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
             frequency varchar(16) NOT NULL,
             team_id INTEGER REFERENCES Team(id)
         );
    ''',
    f'''
         CREATE TABLE EventOccurrence(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             event_id INTEGER REFERENCES Event(id),
             date Date NOT NULL,
             tss REAL NOT NULL
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
            id = self.add_new_event(e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7])
            event = self.event_for_id(id)
            event.generate_occurrences()

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

    def events_for_team(self, team_id):
        from . import Event
        sql = f'''
            SELECT {','.join(Event.db_columns())}
            FROM Event
            WHERE team_id={team_id}
        '''
        return self.__events_for_sql(sql)

    def event_for_id(self, event_id):
        from . import Event
        sql = f'''
            SELECT {','.join(Event.db_columns())}
            FROM Event
            WHERE id={event_id}
        '''
        return self.__events_for_sql(sql)[0]

    def update_event(self, event_id, name, start_time, end_time, estimated_rpe, start_date, end_date, frequency, team_id):
        sql = f'''
            UPDATE Event
            SET
            name='{name}', start_time='{start_time}', end_time='{end_time}', estimated_rpe={estimated_rpe}, 
            start_date='{start_date}', end_date='{end_date}', frequency='{frequency}', team_id='{team_id}'
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

    def event_occurrences(self, event_id):
        sql = f'''
            SELECT id, event_id, date, tss
            FROM EventOccurrence
            WHERE event_id={event_id}
        '''
        return self.__event_occurrences_for_sql(sql)

    def event_occurrence_exists(self, event_id, date):
        sql = f'''
            SELECT id FROM EventOccurrence
            WHERE event_id={event_id} AND date='{date}'
        '''
        occurrences = self.__conn.execute(sql).fetchall()
        return len(occurrences) > 0

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

    def add_new_event(self, event_name, start_time, end_time, estimated_rpe, start_date, end_date, frequency, team_id):
        sql = f'''
            INSERT INTO Event
            (name, start_time, end_time, estimated_rpe, start_date, end_date, frequency, team_id)
            VALUES
            ('{event_name}', '{start_time}', '{end_time}', {estimated_rpe}, '{start_date}', '{end_date}', '{frequency}', 
            {team_id})
         ;
        '''
        self.__conn.execute(sql)
        self.__conn.commit()
        last_id = self.__conn.execute('SELECT last_insert_rowid()').fetchall()[0][0]
        return last_id

    def add_new_event_occurrency(self, event_id, date, tss):
        sql = f'''
            INSERT INTO EventOccurrence
            (event_id, date, tss)
            VALUES
            ({event_id}, '{date}', {tss})
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

    def remove_event_for_id(self, event_id):
        sql = f'DELETE FROM Event WHERE id={event_id}'
        self.__conn.execute(sql)
        self.__conn.commit()
        # remove associated occurences
        sql = f'DELETE FROM EventOccurrence WHERE event_id={event_id}'
        self.__conn.execute(sql)
        self.__conn.commit()

    def __add_new_team_player(self, team_id, player_id):
        sql = f'''
            INSERT INTO TeamPlayer
            (team_id, player_id)
            VALUES
            ({team_id}, {player_id})
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
        from . import EventOccurrence
        return [EventOccurrence(*e) for e in events]

if __name__ == '__main__':
    print('Running')
    DatabaseManager().create_db()