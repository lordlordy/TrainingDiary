from django.conf import settings
import sqlite3
import os

from pandas.io.sql import DatabaseError

import trainingdiary
from workoutentry.modelling.time_period import TimePeriod
from workoutentry.models import Day, Reading, Workout, RaceResult
from datetime import datetime
from dateutil import parser
import pandas as pd

workout_select_sql = f'''
        SELECT primary_key, date, workout_number, activity, activity_type, equipment, seconds, rpe, tss, 
             tss_method, km, kj, ascent_metres, reps, is_race, cadence, watts, watts_estimated, heart_rate, 
             is_brick, keywords, comments, last_save
        FROM Workout
    '''

race_result_select_sql = f'''
        SELECT primary_key, date, race_number, type, brand, distance, name, category, overall_position, 
        category_position, swim_seconds, t1_seconds, bike_seconds, t2_seconds, run_seconds, swim_km, bike_km, run_km, 
        comments, race_report, last_save
        FROM RaceResult
    '''


class TrainingDataManager:

    def __init__(self, db_name=None):
        if db_name is None:
            self.__db_name = settings.DATABASES['training_data_db']['NAME']
        else:
            self.__db_name = db_name

        db_path = os.path.join(trainingdiary.BASE_DIR, self.__db_name)
        self.__conn = sqlite3.connect(db_path)

    def diary_time_period(self) -> TimePeriod:
        start = parser.parse(self.earliest_date()).date()
        end = parser.parse(self.latest_date()).date()
        return TimePeriod(start, end)

    def latest_date(self):
        sql = 'SELECT date FROM Day ORDER BY date DESC LIMIT 1'
        date = self.__conn.execute(sql).fetchall()[0][0]
        return date

    def earliest_date(self):
        sql = 'SELECT date FROM Day ORDER BY date ASC LIMIT 1'
        date = self.__conn.execute(sql).fetchall()[0][0]
        return date

    def days(self):
        days = self.__conn.execute('SELECT date, type, comments FROM Day ORDER BY date ASC').fetchall()
        return [Day(*d) for d in days]

    def day_for_date(self, date):
        days = self.__conn.execute(f'SELECT date, type, comments FROM Day WHERE date="{str(date)}"').fetchall()
        if len(days) > 0:
            day = days[0]
            return Day(*day)

    def days_since(self, from_date):
        days = self.__conn.execute(f'SELECT date, type, comments FROM Day WHERE date>="{str(from_date)}"')
        return [Day(*d) for d in days]

    def days_between(self, from_date, to_date):
        days = self.__conn.execute(f'SELECT date, type, comments FROM Day WHERE date>="{str(from_date)}" AND date<="{str(to_date)}"')
        return [Day(*d) for d in days]

    def day_exists(self, date):
        count = self.__conn.execute(f'SELECT COUNT(1) FROM Day WHERE date="{date}"').fetchall()[0][0]
        return count > 0

    def update_day(self, date, day_type, comments):
        sql = f"""
            UPDATE Day
            SET type="{day_type}", comments="{comments}"
            WHERE date="{date}"
        """
        self.__conn.execute(sql)
        self.__conn.commit()

    def save_day(self, date, type, comments):
        sql = f"""
            INSERT INTO Day
            (date, type, comments)
            VALUES
            ("{date}", "{type}", "{comments}")
        """
        self.__conn.execute(sql)
        self.__conn.commit()

    def delete_day(self, date):
        # must delete readings and workouts for this date
        sql = f'''
            DELETE FROM Workout
            WHERE date="{str(date)}"
            '''
        self.__conn.execute(sql)

        sql = f'''
            DELETE FROM RaceResult
            WHERE date="{str(date)}"
            '''
        self.__conn.execute(sql)

        sql = f'''
            DELETE FROM Reading
            WHERE date="{str(date)}"
            '''
        self.__conn.execute(sql)

        sql = f'''
            DELETE FROM Day
            WHERE date="{str(date)}"
            '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def workouts(self):
        workouts = self.__conn.execute(workout_select_sql).fetchall()
        return [Workout(*w) for w in workouts]

    def workouts_between(self, from_date, to_date):
        sql = f'''
            {workout_select_sql}
            WHERE date>='{str(from_date)}' AND date<='{str(to_date)}'
        '''
        workouts = self.__conn.execute(sql)
        return [Workout(*w) for w in workouts]

    def workouts_on_date(self, date):
        sql = f'''
            {workout_select_sql}
            WHERE date="{str(date)}"
        '''

        workouts = self.__conn.execute(sql).fetchall()
        return [Workout(*w) for w in workouts]

    def workout_for_rowid(self, row_id):
        sql = f'''
            {workout_select_sql}
            WHERE rowid={row_id}
        '''
        workouts = self.__conn.execute(sql)
        return [Workout(*w) for w in workouts]

    def workout_for_primary_key(self, primary_key):
        sql = f'''
            {workout_select_sql}
            WHERE primary_key="{primary_key}"
        '''
        workouts = self.__conn.execute(sql)
        return [Workout(*w) for w in workouts]


    def workout_for_date_and_number(self, date, number):
        sql = f'''
            {workout_select_sql}
            WHERE date="{str(date)}" AND workout_number={number}
        '''
        workouts = self.__conn.execute(sql)
        return [Workout(*w) for w in workouts]

    def delete_workout_for_primary_key(self, primary_key):
        sql = f'''
            DELETE FROM Workout
            WHERE primary_key="{primary_key}"
        '''
        curr = self.__conn.cursor()
        curr.execute(sql)
        self.__conn.commit()
        return curr.lastrowid

    def delete_workout(self, date, number):
        sql = f'''
            DELETE FROM Workout
            WHERE date="{str(date)}" AND workout_number={number}
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def update_workout(self, primary_key, activity, activity_type, equipment, seconds, rpe, tss,
             tss_method, km, kj, ascent_metres, reps, is_race, cadence, watts, watts_estimated, heart_rate,
             is_brick, keywords, comments):

        sql = f"""
            UPDATE Workout
            SET activity="{activity}", activity_type="{activity_type}", equipment="{equipment}", seconds={seconds}, 
            rpe={rpe}, tss={tss}, tss_method="{tss_method}", km={km}, kj={kj}, ascent_metres={ascent_metres}, 
            reps={reps}, is_race={is_race}, cadence={cadence}, watts={watts}, watts_estimated={watts_estimated}, 
            heart_rate={heart_rate}, is_brick={is_brick}, keywords="{keywords}", comments="{comments}", 
            last_save="{datetime.now()}"
            WHERE primary_key="{primary_key}"
        """
        cursor = self.__conn.cursor()
        cursor.execute(sql)
        self.__conn.commit()

    def workout_primary_key(self, date, workout_number) -> str:
        return f"{date}-{workout_number}"

    def save_workout(self, date, activity, activity_type, equipment, seconds, rpe, tss,
             tss_method, km, kj, ascent_metres, reps, is_race, cadence, watts, watts_estimated, heart_rate,
             is_brick, keywords, comments):

        workout_number = len(self.workouts_on_date(date)) + 1
        primary_key = self.workout_primary_key(date, workout_number)

        sql = f"""
            INSERT INTO Workout
            (primary_key, date, workout_number, activity, activity_type, equipment, seconds, rpe, tss, tss_method, km, 
            kj, ascent_metres, reps, is_race, cadence, watts, watts_estimated, heart_rate, is_brick, keywords, comments, 
            last_save)
            VALUES
            ("{primary_key}", "{date}", {workout_number}, "{activity}", "{activity_type}", "{equipment}", 
            {seconds}, {rpe}, {tss}, "{tss_method}", {km}, {kj}, {ascent_metres}, {reps}, {is_race}, {cadence}, {watts}, 
            {watts_estimated}, {heart_rate}, {is_brick}, "{keywords}", "{comments}", "{datetime.now()}")
        """
        print(sql)
        cursor = self.__conn.cursor()
        cursor.execute(sql)
        self.__conn.commit()
        return cursor.lastrowid

    def delete_workout(self, date, workout_number):
        sql = f'''
            DELETE FROM Workout
            WHERE date="{str(date)}" AND workout_number={workout_number}
        '''
        # print(sql)
        self.__conn.execute(sql)
        self.__conn.commit()

    def readings(self):
        readings = self.__conn.execute('SELECT date, type, value, primary_key FROM Reading').fetchall()
        return [Reading(*r) for r in readings]

    def reading_for_primary_key(self, primary_key):
        reading = self.__conn.execute(f'SELECT date, type, value, primary_key FROM Reading WHERE primary_key="{primary_key}"').fetchall()[0]
        return Reading(*reading)

    def readings_for_date(self, date):
        readings = self.__conn.execute(f'SELECT date, type, value, primary_key FROM Reading WHERE date="{str(date)}"').fetchall()
        return [Reading(*r) for r in readings]

    def readings_between(self, from_date, to_date):
        readings = self.__conn.execute(f'SELECT date, type, value, primary_key FROM Reading WHERE date>="{str(from_date)}" AND date<="{str(to_date)}"').fetchall()
        return [Reading(*r) for r in readings]

    def unused_readings_for_date(self, date):
        all_readings = self.readings()
        readings_taken = [r.reading_type for r in self.readings_for_date(date)]
        result = []
        for r in all_readings:
            if r.reading_type not in readings_taken:
                result.append(r)
        return result

    def reading_for_date_and_type(self, date, reading_type):
        readings = self.__conn.execute(f'SELECT date, type, value, primary_key FROM Reading WHERE date="{str(date)}" AND type="{reading_type}"').fetchall()
        return [Reading(*r) for r in readings]

    def delete_reading(self, date, reading_type):
        sql = f'''
            DELETE FROM Reading
            WHERE date="{str(date)}" AND type="{reading_type}"
        '''
        # print(sql)
        self.__conn.execute(sql)
        self.__conn.commit()

    def delete_reading_for_primary_key(self, primary_key):
        sql = f'''
              DELETE FROM Reading
              WHERE primary_key="{primary_key}"
          '''
        curr = self.__conn.cursor()
        curr.execute(sql)
        self.__conn.commit()

    def update_reading_for_primary_key(self, primary_key, value):
        sql = f'UPDATE Reading SET value="{value}" WHERE primary_key="{primary_key}"'
        self.__conn.execute(sql)
        self.__conn.commit()

    def update_reading(self, date, reading_type, value):
        sql = f"""
            UPDATE Reading
            SET value="{value}"
            WHERE date="{date}" AND type="{reading_type}"
        """
        self.__conn.execute(sql)
        self.__conn.commit()

    def save_reading(self, date, reading_type, value):
        sql = f"""
            INSERT INTO Reading
            (primary_key, date, type, value)
            VALUES
            ('{date}-{reading_type}','{date}', '{reading_type}', {value})
        """
        self.__conn.execute(sql)
        self.__conn.commit()

    def race_results(self):
        r_results = self.__conn.execute(race_result_select_sql).fetchall()
        return [RaceResult(*r) for r in r_results]

    def future_races(self):
        sql = f'''
                    {race_result_select_sql}
                    WHERE date>="{str(datetime.now().date())}"
                '''
        r_results = self.__conn.execute(sql)
        return [RaceResult(*r) for r in r_results]

    def race_results_of_distance(self, distance):
        sql = f'''
                    {race_result_select_sql}
                    WHERE distance="{str(distance)}"
                '''
        r_results = self.__conn.execute(sql)
        return [RaceResult(*r) for r in r_results]

    def race_results_of_type(self, type):
        sql = f'''
                    {race_result_select_sql}
                    WHERE type="{str(type)}"
                '''
        r_results = self.__conn.execute(sql)
        return [RaceResult(*r) for r in r_results]

    def race_result_for_date_and_number(self, date, number):
        sql = f'''
            {race_result_select_sql}
            WHERE date="{str(date)}" AND race_number={number}
        '''
        r_results = self.__conn.execute(sql).fetchall()
        if len(r_results) > 0:
            r = r_results[0]
            return RaceResult(*r)

    def race_results_between(self, from_date, to_date):
        sql = f'''
            {race_result_select_sql}
            WHERE date>="{str(from_date)}" AND date<="{str(to_date)}"
        '''
        # print(sql)
        r_results = self.__conn.execute(sql)
        return [RaceResult(*r) for r in r_results]

    def delete_race_result(self, date, number):
        sql = f'''
            DELETE FROM RaceResult
            WHERE date="{str(date)}" AND race_number={number}
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def update_race_result(self, date, race_number, race_type, brand, distance, name, category, overall_position,
                           category_position, swim_seconds, t1_seconds, bike_seconds, t2_seconds, run_seconds, swim_km,
                           bike_km, run_km, comments, race_report):
        sql = f"""
            UPDATE RaceResult
            SET  type="{race_type}", brand="{brand}", distance="{distance}", name="{name}", category="{category}", 
            overall_position={overall_position}, category_position={category_position}, swim_seconds={swim_seconds}, 
            t1_seconds={t1_seconds}, bike_seconds={bike_seconds}, t2_seconds={t2_seconds}, run_seconds={run_seconds}, 
            swim_km={swim_km}, bike_km={bike_km}, run_km={run_km}, comments="{comments}", 
            race_report="{race_report}", last_save="{datetime.now()}"
            WHERE date="{date}" AND race_number={race_number}
        """
        self.__conn.execute(sql)
        self.__conn.commit()

    def save_race_result(self, date, race_number, race_type, brand, distance, name, category, overall_position,
                          category_position, swim_seconds, t1_seconds, bike_seconds, t2_seconds, run_seconds, swim_km,
                          bike_km, run_km, comments, race_report):

        if race_number is None:
            # figure out race number
            max_number = self.__conn.execute(f'SELECT max(race_number) FROM RaceResult WHERE date="{date}"').fetchall()[0][0]
            if max_number is None:
                r_number = 1
            else:
                r_number = max_number + 1
        else:
            r_number = race_number

        sql = f"""
            INSERT INTO RaceResult
            (primary_key, date, race_number, type, brand, distance, name, category, overall_position, category_position, 
            swim_seconds, t1_seconds, bike_seconds, t2_seconds, run_seconds, swim_km, bike_km, run_km, comments, 
            race_report, last_save)
            VALUES
            ("{str(date)}-{r_number}", "{str(date)}", {r_number}, "{race_type}", "{brand}", "{distance}", "{name}", 
            "{category}", {overall_position}, {category_position}, {swim_seconds}, {t1_seconds}, {bike_seconds}, 
            {t2_seconds}, {run_seconds}, {swim_km}, {bike_km}, {run_km}, "{comments}", "{race_report}", 
            "{datetime.now()}")
        """
        # print(sql)
        self.__conn.execute(sql)
        self.__conn.commit()

    def day_types(self):
        types = self.__conn.execute('SELECT DISTINCT type FROM Day').fetchall()
        return [t[0] for t in types]

    def equipment_types(self):
        types = self.__conn.execute('SELECT DISTINCT equipment FROM Workout').fetchall()
        return [t[0] for t in types]

    def activities(self):
        types = self.__conn.execute('SELECT DISTINCT activity FROM Workout').fetchall()
        return [t[0] for t in types]

    def activity_types(self):
        types = self.__conn.execute('SELECT DISTINCT activity_type FROM Workout').fetchall()
        return [t[0] for t in types]

    def tss_methods(self):
        types = self.__conn.execute('SELECT DISTINCT tss_method FROM Workout').fetchall()
        return [t[0] for t in types]

    def reading_types(self):
        types = self.__conn.execute('SELECT DISTINCT type FROM Reading').fetchall()
        return [t[0] for t in types]

    def reading_types_unused_for_date(self, date):
        types_used = self.__conn.execute(f'SELECT DISTINCT type FROM Reading WHERE date="{date}"').fetchall()
        types_used = [t[0] for t in types_used]
        result = []
        for r in self.reading_types():
            if r not in types_used:
                result.append(r)
        return result

    def race_types(self):
        types = self.__conn.execute('SELECT DISTINCT type FROM RaceResult').fetchall()
        return [t[0] for t in types]

    def race_brands(self):
        types = self.__conn.execute('SELECT DISTINCT brand FROM RaceResult').fetchall()
        return [t[0] for t in types]

    def race_distances(self):
        types = self.__conn.execute('SELECT DISTINCT distance FROM RaceResult').fetchall()
        return [t[0] for t in types]

    def race_categories(self):
        types = self.__conn.execute('SELECT DISTINCT category FROM RaceResult').fetchall()
        return [t[0] for t in types]

    def bike_summary(self):
        sql_str = "Select equipment,strftime('%Y', date) as Year, round(sum(km)) from workout where activity='Bike' group by Year, equipment"
        dd = dict()
        years = set()
        for i in self.__conn.execute(sql_str).fetchall():
            years.add(i[1])
            year_dict = dd.get(i[0], dict())
            year_dict[i[1]] = i[2]
            dd[i[0]] = year_dict
        # fill in zero for missing years
        for k, v in dd.items():
            v['Total'] = sum(v.values())
            for y in years:
                if y not in v:
                    v[y] = 0
        return dd

    def training_annual_summary(self):
        sql_str = "Select activity, strftime('%Y', date) as Year, round(sum(km)), sum(seconds), round(sum(tss)) from workout group by Year, activity"
        dd = dict()
        activities = set()
        for i in self.__conn.execute(sql_str).fetchall():
            activities.add(i[0])
            year_dict = dd.get(i[1], dict())
            year_dict[i[0]] = {'km': i[2], 'seconds': i[3], 'tss': i[4]}
            dd[i[1]] = year_dict
        # fill in missing activities
        for year, values in dd.items():
            for activity in activities:
                if activity not in values:
                    values[activity] = {'km': 0, 'seconds': 0, 'tss': 0}
            totals = {
                'km': sum([values[k]['km'] for k in values.keys()]),
                'seconds': sum([values[k]['seconds'] for k in values.keys()]),
                'tss': sum([values[k]['tss'] for k in values.keys()]),
            }
            values['Total'] = totals

        return dd

    def day_data_df(self, time_period, data_definition):
        sql = data_definition.sql(time_period)
        df = pd.read_sql_query(sql, self.__conn)
        return df

    def table_for_measure(self, measure) -> str:
        if measure in self.reading_types():
            return "Reading"
        return "Workout"
