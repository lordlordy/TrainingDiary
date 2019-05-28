from django.contrib import admin
from workoutentry.models import Day, Workout, RestingHeartRate, SDNN, RMSSD, KG, FatPercentage, RaceResult

# Register your models here.
admin.site.register(Day)
admin.site.register(Workout)
admin.site.register(RestingHeartRate)
admin.site.register(SDNN)
admin.site.register(RMSSD)
admin.site.register(KG)
admin.site.register(FatPercentage)
admin.site.register(RaceResult)