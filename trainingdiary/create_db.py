import sqlite3


conn = sqlite3.connect('training_data_warehouse.sqlite3')
c = conn.cursor()


try:
    c.execute('''CREATE TABLE Tables
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        period VARCHAR(32),
        activity VARCHAR(32),
        activity_type VARCHAR(32),
        equipment VARCHAR(32),
        table_name VARCHAR(100) UNIQUE)
    ''')

except Exception as e:
    print(e)
    pass