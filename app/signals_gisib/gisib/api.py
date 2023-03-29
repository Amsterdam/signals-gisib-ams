from datetime import date

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist


def get_bearer_token() -> str:
    token = cache.get('GISIB_BEARER_TOKEN')
    if token is None:
        endpoint = f'{settings.GISIB_BASE_URI}/Login'
        data = {
            'Username': settings.GISIB_USERNAME,
            'Password': settings.GISIB_PASSWORD,
            'ApiKey': settings.GISIB_APIKEY,
        }
        response = requests.post(endpoint, json=data)
        response.raise_for_status()

        token = response.text
        cache.set('GISIB_BEARER_TOKEN', token, 5 * 60)  # Store token for 5 minutes

    return f'Bearer {token}'


def _headers() -> dict:
    return {'Authorization': get_bearer_token(), }


def get_collection(object_kind_name: str, item_id: int) -> dict:
    endpoint = f'{settings.GISIB_BASE_URI}/Collections/{object_kind_name}/Items/{item_id}'
    response = requests.get(endpoint, headers=_headers())
    response.raise_for_status()

    response_json = response.json()
    feature_count = len(response_json['features'])
    if feature_count == 0:
        raise ObjectDoesNotExist('CollectionItem matching query does not exists.')
    elif feature_count > 1:
        raise MultipleObjectsReturned(f'get_collection returned more than one item -- it returned {feature_count}')
    else:
        return response_json['features'][0]


def get_collections(object_kind_name: str, filters: list = None, offset: int = 0, limit: int = 500) -> dict:
    query_params = {'offset': offset, 'limit': limit}

    if filters:
        endpoint = f'{settings.GISIB_BASE_URI}/Collections/{object_kind_name}/WithFilter/Items'
        response = requests.post(endpoint, params=query_params, json=filters, headers=_headers())
    else:
        endpoint = f'{settings.GISIB_BASE_URI}/Collections/{object_kind_name}/Items'
        response = requests.get(endpoint, params=query_params, headers=_headers())

    response.raise_for_status()

    return response.json()


def get_collection_deleted_items(object_kind_name: str, reference_date: date) -> dict:
    endpoint = f'{settings.GISIB_BASE_URI}/Collections/{object_kind_name}/DeletedItems'
    query_params = {'referenceDate': reference_date.strftime('%Y/%m/%d')}
    response = requests.get(endpoint, params=query_params, headers=_headers())
    response.raise_for_status()

    return response.json()


def post_collection_insert(data: dict) -> dict:
    endpoint = f'{settings.GISIB_BASE_URI}/Collections/Insert'
    response = requests.post(endpoint, json=data, headers=_headers())
    response.raise_for_status()

    return response.json()
