from typing import Tuple

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.utils import timezone

from signals_gisib.gisib.api import get_collection
from signals_gisib.models import CollectionItem, EPRCurative, Signal


def update_epr_curative(epr_curative: EPRCurative) -> Tuple[EPRCurative, bool]:
    """
    Updates the local snapshot of an EPR Curative with the current GISIB version
    """

    updated = False

    try:
        epr_curative_json = get_collection('EPR Curatief', epr_curative.gisib_id)
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return epr_curative, updated

    try:
        collection_item = CollectionItem.objects.get(gisib_id=epr_curative.gisib_id,
                                                     object_kind_name='EPR Curatief')
    except CollectionItem.DoesNotExist:
        collection_item = CollectionItem.objects.create(gisib_id=epr_curative.gisib_id,
                                                        object_kind_name='EPR Curatief',
                                                        properties=epr_curative_json['properties'],
                                                        raw_properties=epr_curative_json['properties'])
        updated = True
    else:
        if collection_item.raw_properties['LastUpdate'] < epr_curative_json['properties']['LastUpdate']:
            collection_item.properties = epr_curative_json['properties']
            collection_item.raw_properties = epr_curative_json['properties']
            collection_item.save()
            updated = True

    epr_curative.last_checked = timezone.now()

    if not epr_curative.collection_item:
        epr_curative.collection_item = collection_item

    epr_curative.save()

    epr_curative.refresh_from_db()
    return epr_curative, updated


def update_epr_curatives_for_signal(signal: Signal) -> Tuple[Signal, bool]:
    """
    Updates the local snapshots of all EPR Curatives created for the Signal with the current GISIB versions
    """
    updated = False

    for epr_curative in signal.epr_curative.filter(processed=False):
        _, epr_curative_updated = update_epr_curative(epr_curative)
        updated |= epr_curative_updated

    signal.refresh_from_db()
    return signal, updated
