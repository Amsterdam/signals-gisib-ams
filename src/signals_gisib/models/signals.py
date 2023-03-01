from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords


class Signal(models.Model):
    # Minimum data needed of the Signal
    signal_id = models.BigIntegerField()
    signal_geometry = models.PointField()
    signal_created_at = models.DateTimeField()
    signal_extra_properties = models.JSONField()

    # The GISIB flow, at this moment the only flow available is the EPR Curative flow
    flow = models.CharField(max_length=32, choices=(('EPR', 'EPR Curative'), ), null=True, blank=True)

    # True if the flow has been processed, False otherwise
    processed = models.BooleanField(default=False)

    # Track history
    history = HistoricalRecords()
