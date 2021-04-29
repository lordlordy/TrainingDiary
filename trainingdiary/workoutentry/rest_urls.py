from django.urls import path, include

from workoutentry.views.guardian.gatekeeper import check_and_forward
from workoutentry.views.me.table_edit import table_edit_reading

urlpatterns = [

    path('guardian/', include((
        [
            path('anyone/', check_and_forward),
            path('me/', check_and_forward),
            path('me/reading/edit/', table_edit_reading),

        ], 'workoutentry'), namespace='guardian')),

]