from django.shortcuts import render
from workoutentry.forms import EddingtonNumberForm
from workoutentry.data_warehouse import DataWarehouse
import sqlite3
import pandas as pd

def eddington_view(request):

    headings = []
    data = []

    if request.method == 'POST':
        table_name = f'DAY_{request.POST["activity"]}_{request.POST["activity_type"]}_{request.POST["equipment"]}'
        print(table_name)
        conn = sqlite3.connect('training_data_warehouse.db')
        sql_str = f'''
            SELECT * FROM {table_name}
        '''
        result = conn.execute(sql_str)



        col_name = {d[0] for d in result.description}
        col_name.remove('id')
        col_name.remove('date')
        col_name.remove('is_race')
        col_name.remove('brick')
        col_name.remove('watts_estimated')
        print(col_name)
        data = []
        for r in result.fetchall():
            data.append(r)

        # print(data)

        # df = pd.DataFrame(data=data, index=[0,1], columns=result.description)
        df = pd.read_sql_query(sql_str,conn)
        # df.fillna(0, inplace=True)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)

        print(df)
        print(df.dtypes)
        print(type(df.dtypes))
        print(df.index)

        headings = [d[0] for d in result.description]
        dw = DataWarehouse.instance()

    return render(request, 'workoutentry/eddington_numbers.html', {'selection_form': EddingtonNumberForm(),
                                                                   'headings': headings,
                                                                   'data': data})
