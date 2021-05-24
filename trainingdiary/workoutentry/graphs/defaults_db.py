import sqlite3

# from trainingdiary.settings import DATABASES
from workoutentry.graphs.graph_defaults import TimeSeriesDefaults

CHART_DEFAULT_COLS = ['id', 'unique_key', 'label', 'chart_type', 'borderColor', 'backgroundColor', 'fill', 'pointRadius', 'pointHoverRadius',
                      'showLine', 'position', 'number', 'scale_type', 'draw_grid_lines']


class ChartDefaultsManager:

    def __init__(self, db_name=None):
        if db_name is None:
            self.__db_name = "chart_defaults.sqlite3"
        else:
            self.__db_name = db_name

        # db_path = os.path.join(trainingdiary.BASE_DIR, self.__db_name)
        self.__conn = sqlite3.connect(self.__db_name)

    def key_exists(self, key):
        count = self.__conn.execute(f'SELECT COUNT(1) FROM chart_defaults WHERE unique_key="{key}"').fetchall()[0][0]
        return count > 0

    def get_defaults(self):
        sql = f"""
            SELECT {', '.join(CHART_DEFAULT_COLS)}
            FROM chart_defaults
        """
        defaults = self.__conn.execute(sql)
        return [TimeSeriesDefaults.create(**self.__create_defaults_dict(*d)) for d in defaults]

    def get_default(self, unique_key):
        sql = f"""
            SELECT {', '.join(CHART_DEFAULT_COLS)}
            FROM chart_defaults
            WHERE unique_key='{unique_key}'
        """
        defaults = self.__conn.execute(sql)
        return [TimeSeriesDefaults.create(**self.__create_defaults_dict(*d)) for d in defaults]

    def __create_defaults_dict(self, *args) -> dict:
        return {CHART_DEFAULT_COLS[i]: args[i] for i in range(len(CHART_DEFAULT_COLS))}

    def save_defaults(self, unique_key, chart_type, borderColor, backgroundColor, fill, pointRadius, pointHoverRadius, showLine,
                      position, number, scale_type, draw_grid_lines, label="generate"):

        if self.key_exists(unique_key):

            sql = f"""
                UPDATE chart_defaults
                SET
                chart_type='{chart_type}', borderColor='{borderColor}', backgroundColor='{backgroundColor}', fill={fill}, 
                pointRadius={pointRadius}, pointHoverRadius={pointHoverRadius}, showLine={showLine},
                position='{position}', number={number}, scale_type='{scale_type}', draw_grid_lines={draw_grid_lines}, label='{label}'
                WHERE unique_key='{unique_key}'
            """

        else:

            sql = f"""
                INSERT INTO chart_defaults
                (unique_key, chart_type, borderColor, backgroundColor, fill, pointRadius, pointHoverRadius, showLine,
                          position, number, scale_type, draw_grid_lines, label)
                VALUES
                ('{unique_key}', '{chart_type}', '{borderColor}', '{backgroundColor}', {fill}, {pointRadius}, {pointHoverRadius}, {showLine},
                          '{position}', {number}, '{scale_type}', {draw_grid_lines}, '{label}')
            """

        print(sql)
        cursor = self.__conn.cursor()
        cursor.execute(sql)
        self.__conn.commit()

    # def update_defaults(self, for_unique_key, chart_type, borderColor, backgroundColor, fill, pointRadius, pointHoverRadius, showLine,
    #                   position, number, scale_type, draw_grid_lines):
    #
    #     sql = f"""
    #         UPDATE chart_defaults
    #         SET
    #         chart_type='{chart_type}', borderColor='{borderColor}', backgroundColor='{backgroundColor}', fill={fill},
    #         pointRadius={pointRadius}, pointHoverRadius={pointHoverRadius}, showLine={showLine},
    #         position={position}, number={number}, scale_type='{scale_type}', draw_grid_lines={draw_grid_lines}
    #         WHERE unique_key='{for_unique_key}'
    #     """
    #     print(sql)
    #     cursor = self.__conn.cursor()
    #     cursor.execute(sql)
    #     self.__conn.commit()

    def delete_defaults(self, unique_key):
        sql = f'''
            DELETE FROM chart_defaults
            WHERE unique_key='{unique_key}'
        '''
        self.__conn.execute(sql)
        self.__conn.commit()