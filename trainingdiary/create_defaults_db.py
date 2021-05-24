import sqlite3

from trainingdiary.settings import CHART_DEFAULTS_DB

conn = sqlite3.connect(CHART_DEFAULTS_DB)
c = conn.cursor()

def create_chart_defaults():

    try:
        c.execute('''CREATE TABLE chart_defaults
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            unique_key TEXT UNIQUE,
            label TEXT,
            chart_type TEXT,
            borderColor TEXT,
            backgroundCOlor TEXT,
            fill BOOLEAN,
            pointRadius INTEGER,
            pointHoverRadius INTEGER,
            showLine BOOLEAN,
            position TEXT,
            number INTEGER,
            scale_type TEXT,
            draw_grid_lines BOOLEAN
            )
        ''')

    except Exception as e:
        print(e)
        pass