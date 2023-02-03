from django.contrib.gis.db import models
from django.db.models import CASCADE
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


class EPRCurative(models.Model):
    signal = models.ForeignKey(to='Signal', related_name='epr_curative', on_delete=CASCADE)
    collection_item = models.ForeignKey(to='CollectionItem', related_name='+', on_delete=CASCADE, null=True, blank=True)

    gisib_id = models.BigIntegerField()

    original_request = models.JSONField()
    original_response = models.JSONField()

    status_id = models.BigIntegerField(null=True, blank=True)
    processed = models.BooleanField(default=False)

    last_checked = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return f'{self.gisib_id} ({self.get_status_display()})'

    def get_status_display(self):
        try:
            collection_item = CollectionItem.objects.get(gisib_id=self.status_id, object_kind_name='Registratie EPR')
        except CollectionItem.DoesNotExist:
            return 'unknown'
        else:
            return collection_item.raw_properties['Description']
