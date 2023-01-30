from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from signals_gisib.models import Signal
from signals_gisib.models.gisib import CollectionItem


class CollectionItemAdmin(SimpleHistoryAdmin):
    list_display = ('gisib_id', 'object_kind_name', 'created_at')
    list_filter = ('object_kind_name', )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(CollectionItem, CollectionItemAdmin)
admin.site.register(Signal, SimpleHistoryAdmin)
