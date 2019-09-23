from django.conf import settings
import sqlite3
import os
import trainingdiary
from workoutentry.models import Day, Reading, Workout, RaceResult
import datetime

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

    def latest_date(self):
        sql = 'SELECT date FROM Day ORDER BY date DESC LIMIT 1'
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

    def workout_for_date_and_number(self, date, number):
        sql = f'''
            {workout_select_sql}
            WHERE date="{str(date)}" AND workout_number={number}
        '''
        workouts = self.__conn.execute(sql)
        return [Workout(*w) for w in workouts]

    def delete_workout(self, date, number):
        sql = f'''
            DELETE FROM Workout
            WHERE date="{str(date)}" AND workout_number={number}
        '''
        self.__conn.execute(sql)
        self.__conn.commit()

    def update_workout(self, date, workout_number, activity, activity_type, equipment, seconds, rpe, tss,
             tss_method, km, kj, ascent_metres, reps, is_race, cadence, watts, watts_estimated, heart_rate,
             is_brick, keywords, comments):

        sql = f"""
            UPDATE Workout
            SET activity="{activity}", activity_type="{activity_type}", equipment="{equipment}", seconds={seconds}, 
            rpe={rpe}, tss={tss}, tss_method="{tss_method}", km={km}, kj={kj}, ascent_metres={ascent_metres}, 
            reps={reps}, is_race={is_race}, cadence={cadence}, watts={watts}, watts_estimated={watts_estimated}, 
            heart_rate={heart_rate}, is_brick={is_brick}, keywords="{keywords}", comments="{comments}", 
            last_save="{datetime.datetime.now()}"
            WHERE date="{date}" AND workout_number={workout_number}
        """
        self.__conn.execute(sql)
        self.__conn.commit()

    def save_workout(self, date, activity, activity_type, equipment, seconds, rpe, tss,
             tss_method, km, kj, ascent_metres, reps, is_race, cadence, watts, watts_estimated, heart_rate,
             is_brick, keywords, comments):

        workout_number = len(self.workouts_on_date(date)) + 1

        sql = f"""
            INSERT INTO Workout
            (primary_key, date, workout_number, activity, activity_type, equipment, seconds, rpe, tss, tss_method, km, 
            kj, ascent_metres, reps, is_race, cadence, watts, watts_estimated, heart_rate, is_brick, keywords, comments, 
            last_save)
            VALUES
            ("{date}-{workout_number}", "{date}", {workout_number}, "{activity}", "{activity_type}", "{equipment}", 
            {seconds}, {rpe}, {tss}, "{tss_method}", {km}, {kj}, {ascent_metres}, {reps}, {is_race}, {cadence}, {watts}, 
            {watts_estimated}, {heart_rate}, {is_brick}, "{keywords}", "{comments}", "{datetime.datetime.now()}")
        """
        print(sql)
        self.__conn.execute(sql)
        self.__conn.commit()

    def delete_workout(self, date, workout_number):
        sql = f'''
            DELETE FROM Workout
            WHERE date="{str(date)}" AND workout_number={workout_number}
        '''
        print(sql)
        self.__conn.execute(sql)
        self.__conn.commit()


    def readings(self):
        readings = self.__conn.execute('SELECT date, type, value FROM Reading').fetchall()
        return [Reading(*r) for r in readings]

    def readings_for_date(self, date):
        readings = self.__conn.execute(f'SELECT date, type, value FROM Reading WHERE date="{str(date)}"').fetchall()
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
        readings = self.__conn.execute(f'SELECT date, type, value FROM Reading WHERE date="{str(date)}" AND type="{reading_type}"').fetchall()
        return [Reading(*r) for r in readings]

    def delete_reading(self, date, reading_type):
        sql = f'''
            DELETE FROM Reading
            WHERE date="{str(date)}" AND type="{reading_type}"
        '''
        print(sql)
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
                    WHERE date>="{str(datetime.date.today())}"
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
        print(sql)
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
            race_report="{race_report}", last_save="{datetime.datetime.now()}"
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
            "{datetime.datetime.now()}")
        """
        print(sql)
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