from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin

from signals_gisib.models import Signal
from signals_gisib.models.gisib import CollectionItem, EPRCurative


@admin.register(CollectionItem)
class CollectionItemAdmin(SimpleHistoryAdmin):
    list_display = ('gisib_id', 'object_kind_name', 'created_at')
    list_filter = ('object_kind_name', )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class EPRCurativeInline(admin.TabularInline):
    model = EPRCurative
    can_delete = False
    extra = 0
    fk_name = 'signal'
    fields = ('gisib_id', 'get_status_display', 'last_checked', 'processed', )
    readonly_fields = fields

    def has_add_permission(self, request, obj):
        return False

    @admin.action(description='status')
    def get_status_display(self, obj):
        return obj.get_status_display()


class DateFieldListFilter(admin.SimpleListFilter):
    title = _('Signal created date')
    parameter_name = 'scd'

    def lookups(self, request, model_admin):
        return [
            ('today', _('Today')),
            ('past_week', _('Past 7 days')),
            ('this_month', _('This month')),
            ('past_month', _('Past month')),
        ]

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'today':
            return queryset.filter(signal_created_at__date=now.date())
        if self.value() == 'past_week':
            return queryset.filter(signal_created_at__lte=now, signal_created_at__gte=now-timezone.timedelta(days=7))
        if self.value() == 'this_month':
            return queryset.filter(signal_created_at__month=now.month)
        if self.value() == 'past_month':
            return queryset.filter(signal_created_at__month=now.month-1)


@admin.register(Signal)
class SignalAdmin(SimpleHistoryAdmin):
    search_fields = ('signal_id', )
    list_display = ('signal_id', 'signal_created_at', 'processed', 'get_epr_curative_not_processed_count',
                    'get_epr_curative_processed_count', )
    list_filter = (DateFieldListFilter, )

    readonly_fields = ('signal_id', 'signal_created_at', 'signal_geometry', 'signal_extra_properties', 'processed')

    inlines = (EPRCurativeInline, )

    @admin.display(description='Processed count')
    def get_epr_curative_not_processed_count(self, obj):
        return obj.epr_curative.exclude(processed=True).count()

    @admin.display(description='Not processed count')
    def get_epr_curative_processed_count(self, obj):
        return obj.epr_curative.exclude(processed=False).count()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
