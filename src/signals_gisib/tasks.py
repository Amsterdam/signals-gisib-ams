from datetime import timedelta
from typing import List

from celery import shared_task
from django.http import QueryDict
from django.utils import timezone

from signals_gisib.gisib.import_oak_trees import start_import
from signals_gisib.models.signals import Signal
from signals_gisib.signals.api import get_v1_private_signals


@shared_task
def import_quercus_trees(time_delta: timedelta = None, clear_table: bool = False):
    start_import(time_delta=time_delta, clear_table=clear_table)


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
            Signal.objects.create(signal_id=signal_json['id'], snapshot=signal_json)
