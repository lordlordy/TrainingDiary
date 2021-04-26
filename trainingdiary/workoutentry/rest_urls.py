from django.urls import path, include

from workoutentry.views.guardian.gatekeeper import check_and_forward

urlpatterns = [

    path('guardian/', include((
        [
            path('anyone/', check_and_forward),
            path('me/', check_and_forward),

        ], 'workoutentry'), namespace='guardian')),

]