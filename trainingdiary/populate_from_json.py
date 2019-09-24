import json
import datetime

ALL = 'all'
DAY = 'day'
KG = 'kg'
LBS = 'lbs'
FAT = 'fat'
HR = 'hr'
SDNN = 'sdnn'
RMSSD = 'rmssd'
TSB = 'tsb'
STRAIN = 'strain'
PRINT_PROGRESS = 'pp'

import sys
if __name__ == '__main__':

    all = day = fat = kg = lbs = hr = sdnn = rmssd = tsb = strain = False
    print_progress = False
    if PRINT_PROGRESS in sys.argv:
        print_progress = True

    print(sys.argv)

    if ALL in sys.argv or len(sys.argv) == 0:
        all = True
    if DAY in sys.argv:
        day = True
    if FAT in sys.argv:
        fat = True
    if KG in sys.argv:
        kg = True
    if LBS in sys.argv:
        lbs = True
    if HR in sys.argv:
        hr = True
    if SDNN in sys.argv:
        sdnn = True
    if RMSSD in sys.argv:
        rmssd = True
    if TSB in sys.argv:
        tsb = True
    if STRAIN in sys.argv:
        strain = True


    import workoutentry.data_warehouse as dw
    import os

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db = os.path.join(os.getcwd(), 'training_data_warehouse_TEST.sqlite3')
    f = open('TrainingDiary.json')
    data = json.load(f)

    dwm = dw.DataWarehouseManager(data=data, db_name=db)

    dwm.delete_from_date(datetime.date(2019,5,1))

    if all or day:
        print('Basic day info...')
        dwm.populate_days(print_progress)

    if all or kg:
        print('KG...')
        dwm.populate_kg(print_progress)

    if all or lbs:
        print('LBS...')
        dwm.populate_lbs(print_progress)

    if all or fat:
        print('Fat%...')
        dwm.populate_fat_percent(print_progress)

    if all or hr:
        print('HR...')
        dwm.populate_hr(print_progress)

    if all or sdnn:
        print('SDNN...')
        dwm.populate_sdnn(print_progress)

    if all or rmssd:
        print('RMSSD...')
        dwm.populate_rmssd(print_progress)

    if all or tsb:
        print('Calculating TSB ...')
        dwm.calculate_all_tsb(from_date=None, print_progress=print_progress)

    if all or strain:
        print('Calculating Strain ...')
        dwm.calculate_all_strain(from_date=None, print_progress=print_progress)

