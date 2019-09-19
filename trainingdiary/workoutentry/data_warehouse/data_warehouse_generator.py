import sqlite3
from django.conf import settings
from workoutentry.training_data import TrainingDataManager


class DataWarehouseGenerator:


    def __init__(self, warehouse_name):
        self.__conn = sqlite3.connect(warehouse_name)

        try:
            c = self.__conn.cursor()
            c.execute('''
                        CREATE TABLE Tables(
                        period varchar(16) NOT NULL,
                        activity varchar(16) NOT NULL,
                        activity_type varchar(16) NOT NULL,
                        equipment varchar (16) NOT NULL,
                        table_name varchar(64) NOT NULL,
                        first_date DATE NOT NULL,
                        PRIMARY KEY (table_name));
            ''')

        except Exception as e:
            print(e)
            print("continuing")
            pass

    def generate(self):
        days = TrainingDataManager().days()
        tables = dict()
        for d in days:
            for t in d.workout_types():
                table_name = f"day_{str(t)}"
                if table_name not in tables:
                    self.create_table(table_name, t, d.date)
                    tables[table_name] = t
                    print(table_name)

    def create_table(self, table_name, workout_type, first_date):
        pass