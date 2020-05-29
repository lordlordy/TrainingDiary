from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required

from workoutentry.data_warehouse import DataWarehouseGenerator, DataWarehouse, WarehouseColumn
from workoutentry.training_data import TrainingDataManager
from workoutentry.forms import (DataWarehouseUpdateForm, UpdateDayDataForm, UpdateHRVForm, UpdateTSBForm,
                                UpdateInterpolationForm)

from django.contrib import messages
import datetime
import sqlite3

PRINT_PROGRESS = False

@login_required
def warehouse_management(request, initial=dict()):

    tsb = kg = fat = hr = sdnn = rmssd = hrv = latest = None
    try:
        tsb = DataWarehouse.instance().tsb_to_date()
        kg = DataWarehouse.instance().interpolated_to(WarehouseColumn.kg)
        fat = DataWarehouse.instance().interpolated_to(WarehouseColumn.fat_percentage)
        hr = DataWarehouse.instance().interpolated_to(WarehouseColumn.resting_hr)
        sdnn = DataWarehouse.instance().interpolated_to(WarehouseColumn.sdnn)
        rmssd = DataWarehouse.instance().interpolated_to(WarehouseColumn.rmssd)
        hrv = DataWarehouse.instance().hrv_threshold_to_date()
        latest = DataWarehouse.instance().max_date()
    except sqlite3.OperationalError as e:
        print(e)

    return render(request, 'workoutentry/warehouse_management.html',
                  {'generate_form': DataWarehouseUpdateForm(),
                   'day_form': UpdateDayDataForm(initial=initial),
                   'tsb_form': UpdateTSBForm(initial=initial),
                   'interpolate_form': UpdateInterpolationForm(initial=initial),
                   'hrv_form': UpdateHRVForm(initial=initial),
                   'latest_data_date': TrainingDataManager().latest_date(),
                   'tsb_to_date': tsb,
                   'kg_interpolated_to': kg,
                   'fat_interpolated_to': fat,
                   'hr_interpolated_to': hr,
                   'sdnn_interpolated_to': sdnn,
                   'rmssd_interpolated_to': rmssd,
                   'hrv_threshold_to_date': hrv,
                   'latest_warehouse_date': latest})


def data_warehouse_update(request):
    warehouse_name = settings.DATABASES['data_warehouse_db']['NAME']
    start = datetime.datetime.now()
    DataWarehouseGenerator(warehouse_name).generate_from_date(request.POST['update_warehouse_date'],
                                                              print_progress=PRINT_PROGRESS)
    # messages.info(request, f'Warehouse updated in {datetime.datetime.now() - start}')

    return JsonResponse(data={'time': f'{datetime.datetime.now() - start}'})


def update_days(request):
    warehouse_name = settings.DATABASES['data_warehouse_db']['NAME']
    start = datetime.datetime.now()
    DataWarehouseGenerator(warehouse_name).update_days(request.POST['from_date'],
                                                       request.POST['to_date'],
                                                       print_progress=PRINT_PROGRESS)
    messages.info(request, f"""
        Warehouse days ({request.POST['from_date']} to {request.POST['to_date']}) 
        updated in {datetime.datetime.now() - start}""")

    return warehouse_management(request, initial={'from_date': request.POST['from_date'],
                                                      'to_date': request.POST['to_date']})


def calculate_tsb(request):
    warehouse_name = settings.DATABASES['data_warehouse_db']['NAME']
    start = datetime.datetime.now()

    dwg = DataWarehouseGenerator(warehouse_name)

    if 'table_choice' in request.POST:
        for table in request.POST.getlist('table_choice'):
            start = datetime.datetime.now()
            dwg.populate_tsb_monotony_strain_for_table(table, request.POST['from_date'], request.POST['to_date'])
            print(f'TSB done for {table}')
            messages.info(request, f"""
                Warehouse TSB, Monotony and Strain for {table}
                ({request.POST['from_date']} to {request.POST['to_date']})
                calculated in {datetime.datetime.now() - start}""")
    else:
        dwg.generate_tsb_monotony_strain(request.POST['from_date'], request.POST['to_date'],
                                         print_progress=PRINT_PROGRESS)
        messages.info(request, f"""
            Warehouse TSB, Monotony and Strain
            ({request.POST['from_date']} to {request.POST['to_date']})
            calculated in {datetime.datetime.now() - start}""")

    return warehouse_management(request, initial={'from_date': request.POST['from_date'],
                                                      'to_date': request.POST['to_date']})


def interpolate_values(request):
    warehouse_name = settings.DATABASES['data_warehouse_db']['NAME']
    start = datetime.datetime.now()
    DataWarehouseGenerator(warehouse_name).interpolate_zeroes(request.POST['from_date'],
                                                              request.POST['to_date'],
                                                              request.POST['col_choice'],
                                                              print_progress=PRINT_PROGRESS)
    messages.info(request, f"""
        Warehouse interpolation for {request.POST['col_choice']} 
        ({request.POST['from_date']} to {request.POST['to_date']}) 
        done in {datetime.datetime.now() - start}""")

    return warehouse_management(request, initial={'from_date': request.POST['from_date'],
                                                      'to_date': request.POST['to_date']})


def calculate_hrv(request):
    warehouse_name = settings.DATABASES['data_warehouse_db']['NAME']
    start = datetime.datetime.now()
    DataWarehouseGenerator(warehouse_name).generate_hrv_limits(request.POST['from_date'],
                                                               request.POST['to_date'],
                                                               print_progress=PRINT_PROGRESS)
    messages.info(request, f"""
        Warehouse HRV thresholds ({request.POST['from_date']} to {request.POST['to_date']}) 
        calculated in {datetime.datetime.now() - start}""")

    return warehouse_management(request, initial={'from_date': request.POST['from_date'],
                                                      'to_date': request.POST['to_date']})
