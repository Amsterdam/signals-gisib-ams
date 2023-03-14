from django.test import TransactionTestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time

from signals_gisib.gisib.import_oak_trees import start_import
from signals_gisib.models.gisib import CollectionItem
from signals_gisib.tests.factories import CollectionItemFactory
from signals_gisib.tests.gisib import gisib_api_vcr


@freeze_time('2023-01-24T08:50:00+00:00')
@override_settings(GISIB_ENDPOINT='https://amsterdam-test.gisib.nl/api/api', GISIB_USERNAME='test-user',
                   GISIB_PASSWORD='test-password', GISIB_APIKEY='test-api-key', GISIB_LIMIT=2, GISIB_SLEEP=0.5)
class ImportOakTreesTestCase(TransactionTestCase):

    @gisib_api_vcr.use_cassette()
    def test_import_oak_trees_clean(self):
        """
        This test case imports 6 Oak trees and verifies that 2 of the imported Oak trees have been deleted from the
        database, because the 2 trees are marked as deleted in the past 365 days.
        """
        self.assertEqual(CollectionItem.objects.count(), 0)

        start_import(time_delta=None, clear_table=True)

        self.assertEqual(CollectionItem.objects.count(), 4)

    @gisib_api_vcr.use_cassette()
    def test_import_oak_trees_last_X_days(self):
        """
        This test case imports 2 Oak trees, one of which is already exists in the database. The test then verifies that
        both of the imported Oak trees are deleted from the database, because the trees are marked as deleted in the
        past 365 days.
        """
        raw_properties = {'LastUpdate': (timezone.now() - timezone.timedelta(days=365*5)).isoformat()}
        CollectionItemFactory.create(gisib_id=1177728, object_kind_name='Boom', raw_properties=raw_properties)

        self.assertEqual(CollectionItem.objects.count(), 1)

        time_delta = timezone.timedelta(days=365)
        start_import(time_delta=time_delta, clear_table=False)

        self.assertEqual(CollectionItem.objects.count(), 0)

    @gisib_api_vcr.use_cassette()
    def test_import_oak_trees_nothing_to_import(self):
        """
        Nothing to import
        """
        self.assertEqual(CollectionItem.objects.count(), 0)

        time_delta = timezone.timedelta(seconds=1)
        start_import(time_delta=time_delta, clear_table=False)

        self.assertEqual(CollectionItem.objects.count(), 0)

    @gisib_api_vcr.use_cassette()
    def test_import_oak_trees_no_new_and_updated_collection_items(self):
        """
        This test case imports 2 Oak trees, one of which is already exists in the database. The test then verifies that
        both of the imported Oak trees are deleted from the database, because the trees are marked as deleted in the
        past 365 days.
        """
        raw_properties = {'LastUpdate': (timezone.now()).isoformat()}
        ci1 = CollectionItemFactory.create(gisib_id=3749029, object_kind_name='Boom', raw_properties=raw_properties)
        ci2 = CollectionItemFactory.create(gisib_id=1177728, object_kind_name='Boom', raw_properties=raw_properties)

        self.assertEqual(CollectionItem.objects.count(), 2)

        time_delta = timezone.timedelta(days=365)
        start_import(time_delta=time_delta, clear_table=False)

        self.assertEqual(CollectionItem.objects.count(), 2)
        self.assertEqual(CollectionItem.objects.get(pk=ci1.pk).updated_at, ci1.updated_at)
        self.assertEqual(CollectionItem.objects.get(pk=ci2.pk).updated_at, ci2.updated_at)
