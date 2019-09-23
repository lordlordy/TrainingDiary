from django.shortcuts import render
from django.conf import settings

from workoutentry.data_warehouse import DataWarehouseGenerator, DataWarehouse
from workoutentry.training_data import TrainingDataManager
from workoutentry.forms import DBManagementForm

from django.contrib import messages


def data_warehouse_update(request):

    print('bring it on big boy')
    print(request.POST)

    warehouse_name = settings.DATABASES['data_warehouse_db']['NAME']
    DataWarehouseGenerator(warehouse_name).generate_from_date(request.POST['update_warehouse_date'], print_progress=True)


    return render(request, 'workoutentry/diary_upload.html', {'form': DBManagementForm(),
                                                              'latest_data_date': TrainingDataManager().latest_date(),
                                                              'latest_warehouse_date': DataWarehouse.instance().max_date()})
