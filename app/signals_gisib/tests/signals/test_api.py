from unittest.mock import patch

from django.http import QueryDict
from django.test import TestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time
from requests import HTTPError

from signals_gisib.signals.api import get_v1_private_signals, patch_v1_private_signal_status
from signals_gisib.tests.signals import signals_api_vcr


@freeze_time('2023-01-27T14:00:00+00:00')
@override_settings(SIGNALS_ENDPOINT='http://test.com/signals')
class SignalsApiTestCase(TestCase):
    @patch('signals_gisib.signals.api.get_bearer_token')
    @signals_api_vcr.use_cassette()
    def test_get_v1_private_signals(self, mock_get_bearer_token):
        # set the return value of the mocked function
        mock_get_bearer_token.return_value = 'Bearer abcdefg'

        today = timezone.now()
        x_days_ago = today - timezone.timedelta(days=365)

        filters = QueryDict(mutable=True)
        filters.update({'updated_after': x_days_ago.strftime('%Y-%m-%dT%H:%M:%S')})
        filters.update({'status': 'm'})
        filters.update({'category_slug': 'eikenprocessierups'})
        filters.update({'page_size': '1'})

        # call the get_bearer_token function
        signal_json_list = get_v1_private_signals(filters=filters)

        # Check the return value
        self.assertEqual(len(signal_json_list), 2)

    @patch('signals_gisib.signals.api.get_bearer_token')
    @signals_api_vcr.use_cassette()
    def test_get_v1_private_signals_no_signals(self, mock_get_bearer_token):
        # set the return value of the mocked function
        mock_get_bearer_token.return_value = 'Bearer abcdefg'

        # call the get_bearer_token function
        signal_json_list = get_v1_private_signals()

        # Check the return value
        self.assertEqual(len(signal_json_list), 0)

    @override_settings(KEYCLOAK_ENABLED=False)
    @signals_api_vcr.use_cassette()
    def test_get_v1_private_signals_keycloak_disabled_401(self):
        # Data present, but no valid municipal code is supplied
        with self.assertRaises(HTTPError) as cntx:
            # call the get_bearer_token function
            get_v1_private_signals()
        e = cntx.exception
        self.assertIn('401 Client Error: Unauthorized for url:', str(e))

    @patch('signals_gisib.signals.api.get_bearer_token')
    @signals_api_vcr.use_cassette()
    def test_patch_v1_private_signal_status(self, mock_get_bearer_token):
        # set the return value of the mocked function
        mock_get_bearer_token.return_value = 'Bearer abcdefg'

        signal_id = 1

        # Only update the status
        state = 'b'
        response = patch_v1_private_signal_status(signal_id=signal_id, state=state)
        self.assertEqual(response['status']['state'], state)
        self.assertFalse(response['status']['send_email'])
        self.assertIsNone(response['status']['text'])
        self.assertIsNone(response['status']['extra_properties'])

        # Only update the status and add text
        text = 'Lorem ipsum'
        response = patch_v1_private_signal_status(signal_id=signal_id, state=state, text=text)
        self.assertEqual(response['status']['state'], state)
        self.assertFalse(response['status']['send_email'])
        self.assertEqual(response['status']['text'], text)
        self.assertIsNone(response['status']['extra_properties'])

        # Only update the status, add text and extra_properties
        extra_properties = [{'key': 'extra_property_1', 'value': 1}, {'key': 'extra_property_2', 'value': 2}]
        response = patch_v1_private_signal_status(signal_id=signal_id, state=state, text=text,
                                                  extra_properties=extra_properties)
        self.assertEqual(response['status']['state'], state)
        self.assertFalse(response['status']['send_email'])
        self.assertEqual(response['status']['text'], text)
        self.assertEqual(response['status']['extra_properties'], extra_properties)

        # Only update the status to "ready to send" which requires a target_api
        state = 'ready to send'
        target_api = 'gisib'
        response = patch_v1_private_signal_status(signal_id=signal_id, state=state, target_api=target_api)
        self.assertEqual(response['status']['state'], state)
        self.assertFalse(response['status']['send_email'])
        self.assertIsNone(response['status']['text'])
        self.assertIsNone(response['status']['extra_properties'])
        self.assertEqual(response['status']['target_api'], target_api)
