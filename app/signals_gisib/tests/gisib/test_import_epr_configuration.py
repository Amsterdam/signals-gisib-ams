from django.test import TransactionTestCase, override_settings
from freezegun import freeze_time

from signals_gisib.gisib.import_epr_configuration import start_import
from signals_gisib.models.gisib import CollectionItem
from signals_gisib.tests.factories import CollectionItemFactory
from signals_gisib.tests.gisib import gisib_api_vcr


@freeze_time('2023-01-24T08:50:00+00:00')
@override_settings(GISIB_ENDPOINT='https://amsterdam-test.gisib.nl/api/api', GISIB_USERNAME='test-user',
                   GISIB_PASSWORD='test-password', GISIB_APIKEY='test-api-key', GISIB_LIMIT=2, GISIB_SLEEP=0.5)
class ImportEPRConfigurationTestCase(TransactionTestCase):

    @gisib_api_vcr.use_cassette()
    def test_import_epr_configuration_clean(self):
        self.assertEqual(CollectionItem.objects.count(), 0)

        start_import(clear_table=True)

        self.assertEqual(CollectionItem.objects.count(), 13)
        self.assertEqual(CollectionItem.objects.filter(object_kind_name='Registratie EPR').count(), 9)
        self.assertEqual(CollectionItem.objects.filter(object_kind_name='Nestformaat').count(), 4)

    @gisib_api_vcr.use_cassette()
    def test_import_epr_configuration_partially_imported(self):
        # Nestformaat
        nest_collection_items = []
        for gisib_id in [3749027, 3749024]:
            properties = {'Id': gisib_id, 'Code': '1', 'GUID': '{00000000-0000-0000-0000-000000000000}',
                          'IMGeoId': None, 'Revisie': 1, 'LastUpdate': '2022-01-01T00:00:00.00000',
                          'Valid_Till': None, 'Description': 'test'}
            ci = CollectionItemFactory.create(gisib_id=gisib_id, object_kind_name='Nestformaat', geometry=None,
                                              properties=properties, raw_properties=properties)
            nest_collection_items.append(ci)

        # Registratie EPR
        registration_collection_items = []
        for gisib_id in [3749040, 3748950]:
            properties = {'Id': gisib_id, 'Code': '98', 'GUID': '{00000000-0000-0000-0000-000000000000}',
                          'IMGeoId': None, 'Revisie': 1, 'LastUpdate': '2022-01-01T00:00:00.00000',
                          'Valid_Till': None, 'Description': 'test'}
            ci = CollectionItemFactory.create(gisib_id=gisib_id, object_kind_name='Registratie EPR', geometry=None,
                                              properties=properties, raw_properties=properties)
            registration_collection_items.append(ci)

        self.assertEqual(CollectionItem.objects.count(), 4)

        start_import(clear_table=False)

        self.assertEqual(CollectionItem.objects.count(), 13)
        self.assertEqual(CollectionItem.objects.filter(object_kind_name='Registratie EPR').count(), 9)
        self.assertEqual(CollectionItem.objects.filter(object_kind_name='Nestformaat').count(), 4)

    @gisib_api_vcr.use_cassette()
    def test_import_epr_configuration_partially_imported_no_changes(self):
        # Nestformaat
        nest_collection_items = []
        for gisib_id in [3749027, 3749024]:
            properties = {'Id': gisib_id, 'Code': '1', 'GUID': '{00000000-0000-0000-0000-000000000000}',
                          'IMGeoId': None, 'Revisie': 1, 'LastUpdate': '2023-01-01T00:00:00.00000',
                          'Valid_Till': None, 'Description': 'test'}
            ci = CollectionItemFactory.create(gisib_id=gisib_id, object_kind_name='Nestformaat', geometry=None,
                                              properties=properties, raw_properties=properties)
            nest_collection_items.append(ci)

        # Registratie EPR
        registration_collection_items = []
        for gisib_id in [3749040, 3748950]:
            properties = {'Id': gisib_id, 'Code': '98', 'GUID': '{00000000-0000-0000-0000-000000000000}',
                          'IMGeoId': None, 'Revisie': 1, 'LastUpdate': '2023-01-01T00:00:00.00000',
                          'Valid_Till': None, 'Description': 'test'}
            ci = CollectionItemFactory.create(gisib_id=gisib_id, object_kind_name='Registratie EPR', geometry=None,
                                              properties=properties, raw_properties=properties)
            registration_collection_items.append(ci)

        self.assertEqual(CollectionItem.objects.count(), 4)

        start_import(clear_table=False)

        self.assertEqual(CollectionItem.objects.count(), 13)
        self.assertEqual(CollectionItem.objects.filter(object_kind_name='Registratie EPR').count(), 9)
        self.assertEqual(CollectionItem.objects.filter(object_kind_name='Nestformaat').count(), 4)
