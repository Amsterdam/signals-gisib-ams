from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from freezegun import freeze_time

from signals_gisib.models import Signal
from signals_gisib.tasks import import_categorized_signals, import_epr_configuration, import_quercus_trees
from signals_gisib.tests import vcr
from signals_gisib.tests.factories import SignalFactory


class ImportQuercusTreesTest(TestCase):
    @patch('signals_gisib.tasks.start_quercus_trees_import')
    def test_import_quercus_trees(self, start_import_mock):
        # Call the import_quercus_trees function
        import_quercus_trees()

        # Assert that the start_import function was called
        start_import_mock.assert_called_once()

        # Assert that the start_import function was called with the default arguments
        start_import_mock.assert_called_with(time_delta=None, clear_table=False)

    @patch('signals_gisib.tasks.start_quercus_trees_import')
    def test_import_quercus_trees_with_args(self, start_import_mock):
        # Call the import_quercus_trees function with custom arguments
        time_delta = timedelta(days=7)
        import_quercus_trees(time_delta=time_delta, clear_table=True)

        # Assert that the start_import function was called
        start_import_mock.assert_called_once()

        # Assert that the start_import function was called with the custom arguments
        start_import_mock.assert_called_with(time_delta=time_delta, clear_table=True)


class ImportEPRConfigurationTest(TestCase):
    @patch('signals_gisib.tasks.start_epr_configuration_import')
    def test_import_quercus_trees(self, start_import_mock):
        # Call the import_quercus_trees function
        import_epr_configuration()

        # Assert that the start_import function was called
        start_import_mock.assert_called_once()

        # Assert that the start_import function was called with the default arguments
        start_import_mock.assert_called_with(clear_table=False)

    @patch('signals_gisib.tasks.start_epr_configuration_import')
    def test_import_quercus_trees_with_args(self, start_import_mock):
        # Call the import_quercus_trees function with custom arguments
        import_epr_configuration(clear_table=True)

        # Assert that the start_import function was called
        start_import_mock.assert_called_once()

        # Assert that the start_import function was called with the custom arguments
        start_import_mock.assert_called_with(clear_table=True)


@freeze_time('2023-01-27T14:00:00+00:00')
@override_settings(SIGNALS_ENDPOINT='http://test.com/signals')
class ImportCategorizedSignalsTest(TestCase):

    @vcr.use_cassette()
    def test_import_categorized_signals(self):
        self.assertEqual(0, Signal.objects.count())

        category_list = ['eikenprocessierups', ]
        import_categorized_signals(category_list, 365)

        self.assertEqual(2, Signal.objects.count())
        self.assertEqual(2, Signal.objects.filter(signal_id__in=[1, 2]).count())

    @vcr.use_cassette()
    def test_import_categorized_signals_already_imported(self):
        SignalFactory.create(signal_id=1)

        self.assertEqual(1, Signal.objects.count())
        self.assertEqual(1, Signal.objects.filter(signal_id=1).count())

        category_list = ['eikenprocessierups', ]
        import_categorized_signals(category_list, 365)

        self.assertEqual(2, Signal.objects.count())
        self.assertEqual(2, Signal.objects.filter(signal_id__in=[1, 2]).count())

    @vcr.use_cassette()
    def test_import_categorized_signals_no_signals(self):
        self.assertEqual(0, Signal.objects.count())

        category_list = ['overig', ]
        import_categorized_signals(category_list, 365)

        self.assertEqual(0, Signal.objects.count())
