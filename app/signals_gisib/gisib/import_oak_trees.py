import logging
from datetime import datetime, timedelta
from time import sleep
from timeit import default_timer as timer
from typing import List

from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import transaction
from django.utils import timezone

from signals_gisib.gisib.api import get_collection_deleted_items, get_collections
from signals_gisib.models.gisib import CollectionItem

logger = logging.getLogger(__name__)


def _quercus_filter(last_updated: datetime = None) -> List:
    criteria_list = [
        {
            'Property': 'Soortnaam.Description',
            'Value': 'Quercus',
            'Operator': 'StartsWith',
        },
    ]
    if last_updated:
        criteria_list.append({
            'Property': 'LastUpdate',
            'Value': last_updated.strftime('%Y-%m-%dT%H:%M:%S'),
            'Operator': 'GreaterOrEqual',
        })

    return [{'Criterias': criteria_list, 'Operator': 'AND'}]


def _parse_raw_properties(raw_properties: dict) -> dict:
    properties = {
        'species': raw_properties['Soortnaam']['Description']
    }
    return properties


@transaction.atomic
def start_import(time_delta: timedelta = None, clear_table: bool = False):  # noqa C901
    """
    Import Quercus collection
    - Import new items
    - Update existing items (if they have changed since the last import)
    - Delete items (if they have been deleted since the last import)

    :param time_delta:
    :param clear_table:
    :return:
    """
    logger.info('Start import of "Quercus" trees from GISIB')
    logger.info(f'GISIB endpoint: {settings.GISIB_BASE_URI}')

    start = timer()

    _created = 0
    _updated = 0
    _deleted = 0

    if clear_table:
        deleted, _ = CollectionItem.objects.filter(object_kind_name='Boom',
                                                   properties__soort__istartswith='Quercus').delete()
        logger.info(f'Start fresh. Deleted {deleted} "Quercus" trees from the import table.')

    offset = 0
    limit = settings.GISIB_LIMIT

    now = timezone.now()
    if time_delta:
        created_updated_since = now - time_delta
        deleted_since = created_updated_since
    else:
        created_updated_since = None
        deleted_since = now - timedelta(days=365)

    object_kind_name = 'Boom'
    filters = _quercus_filter(last_updated=created_updated_since)

    logger.info(f'Object kind: {object_kind_name}')
    logger.info(f'Object kind filter: {filters}')

    # Create and update items
    collections_json = get_collections(object_kind_name=object_kind_name, filters=filters, offset=offset, limit=limit)
    while len(collections_json['features']) > 0:
        create_collection_items = []
        update_collection_items = []

        for feature_json in collections_json['features']:
            if feature_json['properties']['Longitude'] is None or feature_json['properties']['Latitude'] is None:
                continue

            if not CollectionItem.objects.filter(gisib_id=feature_json['properties']['Id']).exists():
                # Does not exist so create it
                collection_item = CollectionItem(
                    gisib_id=feature_json['properties']['Id'],
                    object_kind_name=object_kind_name,
                    geometry=Point(float(feature_json['properties']['Longitude']),
                                   float(feature_json['properties']['Latitude']),
                                   srid=4326),
                    properties=_parse_raw_properties(feature_json['properties']),
                    raw_properties=feature_json['properties']
                )
                create_collection_items.append(collection_item)
            elif CollectionItem.objects.filter(
                object_kind_name__iexact=object_kind_name,
                gisib_id=feature_json['properties']['Id'],
                raw_properties__LastUpdate__lt=feature_json['properties']['LastUpdate']
            ).exists():
                # Does exist however has been updated since it was imported last time so update it
                collection_item = CollectionItem.objects.get(object_kind_name__iexact=object_kind_name,
                                                             gisib_id=feature_json['properties']['Id'])
                collection_item.properties = _parse_raw_properties(feature_json['properties']),
                collection_item.raw_properties = feature_json['properties']

                update_collection_items.append(collection_item)

        if len(create_collection_items) > 0:
            created = CollectionItem.objects.bulk_create(create_collection_items)
            _created += len(created)

        if len(update_collection_items) > 0:
            updated = CollectionItem.objects.bulk_update(update_collection_items, ['geometry', 'properties'])
            _updated += updated

        logger.debug(f'Sleeping {settings.GISIB_SLEEP} seconds before the next request')
        sleep(settings.GISIB_SLEEP)

        offset += limit
        collections_json = get_collections(object_kind_name=object_kind_name, filters=filters, offset=offset,
                                           limit=limit)

    # Delete items
    deleted_items_json = get_collection_deleted_items(object_kind_name=object_kind_name, reference_date=deleted_since)

    ids_to_delete = [deleted_item['Id'] for deleted_item in deleted_items_json]
    _deleted, _ = CollectionItem.objects.filter(object_kind_name__iexact=object_kind_name,
                                                gisib_id__in=ids_to_delete).delete()

    stop = timer()

    logger.info(f'Created: {_created}')
    logger.info(f'Updated: {_updated}')
    logger.info(f'Deleted: {_deleted}')
    logger.info(f'Time: {stop - start:.2f} second(s)')
    logger.info('Done!')
