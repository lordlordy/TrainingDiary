from django.conf.urls import url

# urlpatterns = [
#     path('', eddington_view, name='eddington_numbers'),
#
# ]

# urlpatterns = url(
#         r'^$', 'django.contrib.staticfiles.views.serve', kwargs={
#             'path': 'index.html', 'document_root': '/static/'}),

from django.urls import path
from workoutentry.views.home import home

urlpatterns = [

    path('', home, name='home'),

]