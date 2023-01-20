from django.urls import path

from health.views import status

urlpatterns = [
    path('', status, name='index'),
]
