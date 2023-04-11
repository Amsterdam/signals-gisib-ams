from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.test import TestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time

from signals_gisib.gisib.api import (
    get_bearer_token,
    get_collection,
    get_collection_deleted_items,
    get_collections,
    post_collection_insert
)
from signals_gisib.tests.gisib import gisib_api_vcr


@freeze_time('2023-01-23T15:40:00+00:00')
@override_settings(GISIB_BASE_URI='https://amsterdam-test.gisib.nl/api/api', GISIB_USERNAME='test-user',
                   GISIB_PASSWORD='test-password', GISIB_APIKEY='test-api-key', GISIB_LIMIT=5, GISIB_SLEEP=0)
class GISIBApiTestCase(TestCase):

    @gisib_api_vcr.use_cassette()
    def test_get_bearer_token(self):
        self.assertEqual(get_bearer_token(), 'Bearer 123456789')

    @gisib_api_vcr.use_cassette()
    def test_get_collections(self):
        filters = [{
            'Criterias': [
                {
                    'Property': 'Soortnaam.Description',
                    'Value': 'Quercus',
                    'Operator': 'StartsWith',
                }
            ],
            'Operator': 'AND'
        }]

        result = get_collections('Boom', filters, 0, 5)
        self.assertEqual(len(result['features']), 5)

    @gisib_api_vcr.use_cassette()
    def test_get_collection_deleted_items(self):
        one_year_ago = timezone.now() - timezone.timedelta(days=365)
        result = get_collection_deleted_items('Boom', one_year_ago.date())

        self.assertEqual(len(result), 2)

    @gisib_api_vcr.use_cassette()
    def test_get_collections_no_filters(self):
        result = get_collections('Boom', None, 0, 5)
        self.assertEqual(len(result['features']), 5)

    @gisib_api_vcr.use_cassette()
    def test_get_collection(self):
        result = get_collection('Boom', 1879642)
        self.assertEqual(result['properties']['Id'], 1879642)

    @gisib_api_vcr.use_cassette()
    def test_get_collection_raises_object_does_not_exist(self):
        with self.assertRaises(ObjectDoesNotExist):
            get_collection('Boom', 1879642)

    @gisib_api_vcr.use_cassette()
    def test_get_collection_raises_multiple_objects_returned(self):
        with self.assertRaises(MultipleObjectsReturned):
            get_collection('Boom', 1879642)

    @gisib_api_vcr.use_cassette()
    def test_post_collection_insert(self):
        data = {
            'Properties': {
                'SIG Nummer melding': 1234567890,
                'Datum melding': timezone.now().strftime('%d-%m-%Y %H:%M'),
                'Nestformaat': 3749024,
                'Boom': 1879642,
            },
            'ObjectKindNaam': 'EPR Curatief'
        }

        result = post_collection_insert(data)

        self.assertIsNone(result['Warnings'])
        self.assertEqual(result['Message'], 'OK')
        self.assertIsNone(result['Errors'])
