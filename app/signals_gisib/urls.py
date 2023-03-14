from django.urls import include, path
from rest_framework.routers import DefaultRouter

from signals_gisib.views import GisibViewSet

router = DefaultRouter()
router.register(r'gisib', GisibViewSet, basename='gisib')

urlpatterns = [
    path('', include((router.urls, 'signals_gisib'), namespace='gisib')),
]
