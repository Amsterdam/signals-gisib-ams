import logging
from timeit import default_timer as timer

from django.conf import settings
from django.db import transaction

from signals_gisib.gisib.api import get_collections
from signals_gisib.models.gisib import CollectionItem

logger = logging.getLogger(__name__)


def _import_registratie_epr():
    """
    Import the "Registratie EPR". This call contains the statuses an EPR Curatief can have in the GISIB system.

    :return:
    """
    _created = 0
    _updated = 0

    # Import "Registratie EPR" configuration, this configuration contains the statuses an EPR Curative can have in GISIB
    # With this configuration a mapping can be made between GISIB statuses and Signals statuses
    object_kind_name = 'Registratie EPR'
    response_json = get_collections(object_kind_name=object_kind_name)

    queryset = CollectionItem.objects.filter(object_kind_name=object_kind_name)
    for item in response_json:
        if not queryset.filter(gisib_id=item['properties']['Id']).exists():
            CollectionItem.objects.create(
                gisib_id=item['properties']['Id'],
                object_kind_name=object_kind_name,
                properties=item['properties'],
                raw_properties=item['properties'],
            )
            _created += 1
        elif queryset.filter(
                gisib_id=item['properties']['Id'],
                raw_properties__LastUpdate__lt=item['properties']['LastUpdate']).exists():
            collection_item = CollectionItem.objects.get(object_kind_name__iexact=object_kind_name,
                                                         gisib_id=item['properties']['Id'])
            collection_item.properties = item['properties']
            collection_item.raw_properties = item['properties']
            collection_item.save()
            _updated += 1

    return _created, _updated


def _import_nestformaat():
    """
    Import the "Nestformaat". This call contains the answers an EPR Curative can have in the GISIS system.

    :return:
    """
    _created = 0
    _updated = 0

    # Import "Nestformaat" configuration, this configuration contains the answers an EPR Curative can have in GISIB
    object_kind_name = 'Nestformaat'
    response_json = get_collections(object_kind_name=object_kind_name)

    queryset = CollectionItem.objects.filter(object_kind_name=object_kind_name)
    for item in response_json:
        if not queryset.filter(gisib_id=item['properties']['Id']).exists():
            CollectionItem.objects.create(
                gisib_id=item['properties']['Id'],
                object_kind_name=object_kind_name,
                properties=item['properties'],
                raw_properties=item['properties'],
            )
            _created += 1
        elif queryset.filter(
                gisib_id=item['properties']['Id'],
                object_kind_name__iexact=object_kind_name,
                raw_properties__LastUpdate__lt=item['properties']['LastUpdate']).exists():
            collection_item = CollectionItem.objects.get(object_kind_name__iexact=object_kind_name,
                                                         gisib_id=item['properties']['Id'])
            collection_item.properties = item['properties']
            collection_item.raw_properties = item['properties']
            collection_item.save()
            _updated += 1

    return _created, _updated


@transaction.atomic
def start_import(clear_table: bool = False):
    """
    Import configuration needed to configure the EPR Curatief flow(s)
    - "Registratie EPR", contains the statuses an EPR Curatief can have in the GISIB system
    - "Nestformaat", contains the answers an EPR Curatief can have in the GISIB system

    :return:
    """
    logger.info('Start import of "EPR" configuration from GISIB')
    logger.info(f'GISIB endpoint: {settings.GISIB_ENDPOINT}')

    start = timer()

    if clear_table:
        deleted, _ = CollectionItem.objects.filter(object_kind_name__in=['Registratie EPR', 'Nestformaat']).delete()
        logger.info(f'Start fresh. Deleted {deleted} items from the table.')

    _created = 0
    _updated = 0

    created_registratie_epr, updated_registratie_epr = _import_registratie_epr()
    _created += created_registratie_epr
    _updated += updated_registratie_epr

    created_nestformaat, updated_nestformaat = _import_nestformaat()
    _created += created_nestformaat
    _updated += updated_nestformaat

    stop = timer()

    logger.info(f'Created: {_created}')
    logger.info(f'Updated: {_updated}')
    logger.info(f'Time: {stop - start:.2f} second(s)')
    logger.info('Done!')
