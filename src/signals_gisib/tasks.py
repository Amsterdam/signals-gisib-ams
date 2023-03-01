from datetime import timedelta
from typing import List

from celery import shared_task
from django.contrib.gis.geos import Point
from django.http import QueryDict
from django.utils import timezone

from signals_gisib.gisib.epr_curative_status import check_status
from signals_gisib.gisib.import_epr_configuration import start_import as start_epr_configuration_import
from signals_gisib.gisib.import_oak_trees import start_import as start_quercus_trees_import
from signals_gisib.models.signals import Signal
from signals_gisib.signals.api import get_v1_private_signals


@shared_task
def import_quercus_trees(time_delta: timedelta = None, clear_table: bool = False):
    start_quercus_trees_import(time_delta=time_delta, clear_table=clear_table)


@shared_task
def import_epr_configuration(clear_table: bool = False):
    start_epr_configuration_import(clear_table=clear_table)


@shared_task
def import_categorized_signals(category_slugs: List[str], time_delta_days: int = 1):
    """
    Imports signals that are in the state "m" (Gemeld in Dutch) and are categorized in one of the provided categories.

    Parameters:
        category_slugs (List[str]): a list of category slugs to filter the signals on
        time_delta_days (int): time_delta_days (default 1)
                               The number of days to look back from the current day to filter the signals
    Returns:
        None
    """
    today = timezone.now()
    x_days_ago = today - timezone.timedelta(days=time_delta_days)

    filters = QueryDict(mutable=True)
    filters.update({'updated_after': x_days_ago.strftime('%Y-%m-%dT%H:%M:%S')})
    filters.update({'status': 'm'})
    for category_slug in category_slugs:
        filters.update({'category_slug': category_slug})

    signal_json_list = get_v1_private_signals(filters=filters)
    for signal_json in signal_json_list:
        signal_qs = Signal.objects.filter(signal_id=signal_json['id'])
        if not signal_qs.exists():
            # The Signal has not yet been imported
            signal_id = signal_json['id']
            signal_geometry = Point(
                signal_json['location']['geometrie']['coordinates'][0],  # longitude
                signal_json['location']['geometrie']['coordinates'][1],  # latitude
            )
            signal_created_at = timezone.datetime.strptime(signal_json['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z')
            signal_extra_properties = signal_json['extra_properties']

            Signal.objects.create(
                signal_id=signal_id,
                signal_geometry=signal_geometry,
                signal_created_at=signal_created_at,
                signal_extra_properties=signal_extra_properties,
            )


@shared_task
def check_epr_curative_status(signal_ids: List[int] = None):
    signals_with_unprocessed_epr_curative_qs = Signal.objects.filter(epr_curative__processed=False)

    if signal_ids:
        # The task has been started with specific signals to check, let's filter them
        signals_with_unprocessed_epr_curative_qs = signals_with_unprocessed_epr_curative_qs.filter(
            signal_id__in=signal_ids
        )

    for signal in signals_with_unprocessed_epr_curative_qs.all().distinct():
        check_status(signal=signal)
