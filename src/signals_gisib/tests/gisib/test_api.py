from django.test import TestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time

from signals_gisib.gisib.api import get_bearer_token, get_collection_deleted_items, get_collections
from signals_gisib.tests.gisib import gisib_api_vcr


@freeze_time('2023-01-23T15:40:00+00:00')
@override_settings(GISIB_ENDPOINT='https://amsterdam-test.gisib.nl/api/api', GISIB_USERNAME='test-user',
                   GISIB_PASSWORD='test-password', GISIB_APIKEY='test-api-key', GISIB_LIMIT=5, GISIB_SLEEP=0)
class GISIBApiTestCase(TestCase):

    @gisib_api_vcr.use_cassette()
    def test_get_bearer_token(self):
        self.assertEqual(get_bearer_token(), 'Bearer eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VybmFtZSI6ImFwaXNpYSIsIkFwaWtleSI6Ijc2MTM0NzBjNDFiMjQ5MGJiYmZlM2YwMWVhMDdmNGY2IiwiZXhwIjoxNjc0NTEzNDc1LCJpc3MiOiJnaXNpYiJ9.udrl3tVRGWO1aPENg4546TkME0-f-8kbWnSVRB-Y_rs')  # noqa

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
