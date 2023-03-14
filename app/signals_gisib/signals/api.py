import logging
from typing import List, Union

import requests
from django.conf import settings
from django.http import QueryDict

from signals_gisib.signals.keycloak import get_bearer_token

logger = logging.getLogger(__name__)


def _headers() -> dict:
    headers = {}
    bearer_token = get_bearer_token()
    if bearer_token:
        headers.update({'Authorization': bearer_token})
    return headers


def get_v1_private_signals(filters: QueryDict = None) -> list:
    endpoint = f'{settings.SIGNALS_ENDPOINT}/v1/private/signals/'
    response = requests.get(endpoint, params=filters, headers=_headers(), verify=False)
    response.raise_for_status()
    response_json = response.json()

    signal_list = []

    while response_json['count'] > 0:
        signal_list += response_json['results']

        if not response_json['_links']['next']['href']:
            break

        response = requests.get(response_json['_links']['next']['href'], headers=_headers(), verify=False)
        response.raise_for_status()
        response_json = response.json()

    return signal_list


def patch_v1_private_signal_status(signal_id: int, state: str, text: str = None, target_api: str = None,
                                   extra_properties: Union[List[dict], dict] = None) -> dict:
    data = {'status': {'state': state, 'send_email': False}}
    if text:
        data['status'].update({'text': text})
    if target_api:
        data['status'].update({'target_api': target_api})
    if extra_properties:
        data['status'].update({'extra_properties': extra_properties})

    endpoint = f'{settings.SIGNALS_ENDPOINT}/v1/private/signals/{signal_id}'
    response = requests.patch(endpoint, json=data, headers=_headers(), verify=False)
    response.raise_for_status()
    response_json = response.json()

    return response_json
