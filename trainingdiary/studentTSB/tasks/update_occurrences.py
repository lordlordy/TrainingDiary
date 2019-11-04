import sqlite3
import os
import datetime

SCHEDULED_ID = 1
COMPLETED_ID = 2

fp = os.path.dirname(os.path.abspath(__file__))
grand_parent = os.path.dirname(os.path.dirname(fp))
db_path = os.path.join(grand_parent, 'TeamTraining.sqlite3')
print(db_path)
conn = sqlite3.connect(db_path)

print(conn.execute('SELECT * FROM Event'))

today = datetime.datetime.now().date()
sql = f'''
    UPDATE PlayerEventOccurrence
    SET state_id='{COMPLETED_ID}'
    WHERE state_id='{SCHEDULED_ID}' AND date <= '{today}'
'''
print(sql)
conn.execute(sql)
conn.commit()
conn.close()