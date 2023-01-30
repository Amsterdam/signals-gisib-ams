from django.db import models
from simple_history.models import HistoricalRecords


class Signal(models.Model):
    # The ID and a snapshot of the Signal when triggered
    signal_id = models.BigIntegerField()
    snapshot = models.JSONField()

    # Track history
    history = HistoricalRecords()
