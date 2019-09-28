import sqlite3
import os
import trainingdiary



class DatabaseManager:
    DB_NAME = 'TeamTraining.sqlite3'






    def create_db(self):
        db_path = os.path.join(trainingdiary.BASE_DIR, DatabaseManager.DB_NAME )
        self.__conn = sqlite3.connect(db_path)



if __name__ == '__main__':
    print('Running')
    DatabaseManager().create_db()