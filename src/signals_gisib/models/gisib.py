from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords


class CollectionItem(models.Model):
    gisib_id = models.BigIntegerField()
    object_kind_name = models.CharField(max_length=255)
    geometry = models.PointField(null=True, blank=True)
    properties = models.JSONField(null=True, blank=True)
    raw_properties = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(editable=False, auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self) -> str:
        return f'{self.gisib_id}'
