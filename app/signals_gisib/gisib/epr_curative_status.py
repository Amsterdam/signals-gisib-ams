from typing import List

from django.conf import settings
from django.utils import timezone

from signals_gisib.gisib.update_epr_curative import update_epr_curatives_for_signal
from signals_gisib.models import CollectionItem, Signal


def _epr_processed_status_list() -> List[int]:
    """
    Returns a list of the ID's of all processed statuses
    """
    return CollectionItem.objects.filter(
        object_kind_name__iexact='Registratie EPR',
        raw_properties__Description__in=settings.GISIB_REGISTRATIE_EPR_PROCESSED_STATUSES
    ).values_list(
        'gisib_id',
        flat=True
    )


def check_status(signal: Signal):
    """
    Check if all EPR Curatives created for the Signal has been processed in GISIB
    """
    if signal.flow != 'EPR':
        # Not in the EPR flow so no need to check
        return

    signal, updated = update_epr_curatives_for_signal(signal=signal)
    if not updated:
        # No changes since last time we checked
        return

    __epr_processed_status_list = _epr_processed_status_list()
    unprocessed_qs = signal.epr_curative.filter(processed=False)
    if unprocessed_qs.exists():
        # There are unprocessed EPR Curatives left, let's check their status
        for epr_curative in unprocessed_qs.all():
            _epr_registration_status = epr_curative.collection_item.raw_properties['Registratie EPR']
            if epr_curative.status_id != _epr_registration_status['Id']:
                # The new status is not the same as the old status, store it and check if it is and end status
                epr_curative.status_id = _epr_registration_status['Id']
                epr_curative.processed = _epr_registration_status['Id'] in __epr_processed_status_list

            epr_curative.save()

    if not unprocessed_qs.exists():
        # All EPR Curative have been processed, the Signal has been processed.
        signal.processed_at = timezone.now()
        signal.save()
