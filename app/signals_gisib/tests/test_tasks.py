from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time

from signals_gisib.models import EPRCurative, Signal
from signals_gisib.tasks import (
    check_epr_curative_status,
    delete_processed_signals,
    import_categorized_signals,
    import_epr_configuration,
    import_quercus_trees
)
from signals_gisib.tests import vcr
from signals_gisib.tests.factories import EPRCurativeFactory, SignalFactory


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
@override_settings(SIGNALS_BASE_URI='http://test.com/signals')
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


class CheckEPRCurativeStatusTest(TestCase):
    @patch('signals_gisib.tasks.check_status')
    def test_run_no_signals(self, check_status_mock):
        check_epr_curative_status()

        # Assert that the start_import function was NOT called
        check_status_mock.assert_not_called()

    @patch('signals_gisib.tasks.check_status')
    def test_run_no_signals_with_unprocessed_epr_curatives(self, check_status_mock):
        test_signals = SignalFactory.create_batch(5)
        for test_signal in test_signals:
            EPRCurativeFactory.create(signal=test_signal, processed=True)

        check_epr_curative_status()

        # Assert that the start_import function was NOT called
        check_status_mock.assert_not_called()

    @patch('signals_gisib.tasks.check_status')
    def test_run_signals_with_unprocessed_epr_curatives(self, check_status_mock):
        test_signals = SignalFactory.create_batch(5)
        for test_signal in test_signals:
            EPRCurativeFactory.create(signal=test_signal, processed=False)

        check_epr_curative_status()

        # Assert that the check_epr_curatives_status function was called with the given signal
        for test_signal in test_signals:
            check_status_mock.assert_any_call(signal=test_signal)

    @patch('signals_gisib.tasks.check_status')
    def test_run_for_specific_signals_with_unprocessed_epr_curatives(self, check_status_mock):
        test_signals = SignalFactory.create_batch(2)
        for test_signal in test_signals:
            EPRCurativeFactory.create(signal=test_signal, processed=False)

        check_epr_curative_status(signal_ids=[test_signal.signal_id for test_signal in test_signals])

        # Assert that the check_epr_curatives_status function was called with the given signal
        for test_signal in test_signals:
            check_status_mock.assert_any_call(signal=test_signal)


@freeze_time('2023-04-05T16:00:00+00:00')
class DeleteProcessedSignalsTest(TestCase):
    def test_delete_progressed_signal(self):
        test_signal = SignalFactory.create(processed_at=timezone.now() - timezone.timedelta(days=2))
        EPRCurativeFactory.create_batch(2, signal=test_signal, processed=True)

        self.assertEqual(1, Signal.objects.count())
        self.assertEqual(2, test_signal.epr_curative.count())
        self.assertEqual(2, EPRCurative.objects.count())

        delete_processed_signals(time_delta_days=1)

        self.assertEqual(0, Signal.objects.count())
        self.assertEqual(0, EPRCurative.objects.count())

    def test_delete_progressed_signal_not_processed(self):
        test_signal = SignalFactory.create()
        EPRCurativeFactory.create_batch(2, signal=test_signal, processed=True)

        self.assertEqual(1, Signal.objects.count())
        self.assertEqual(2, test_signal.epr_curative.count())
        self.assertEqual(2, EPRCurative.objects.count())

        delete_processed_signals(time_delta_days=1)

        self.assertEqual(1, Signal.objects.count())
        self.assertEqual(2, test_signal.epr_curative.count())
        self.assertEqual(2, EPRCurative.objects.count())

    def test_delete_progressed_signal_processed_do_not_delete(self):
        test_signal = SignalFactory.create(processed_at=timezone.now() - timezone.timedelta(days=1))
        EPRCurativeFactory.create_batch(2, signal=test_signal, processed=True)

        self.assertEqual(1, Signal.objects.count())

        delete_processed_signals(time_delta_days=2)

        self.assertEqual(1, Signal.objects.count())
        self.assertEqual(2, test_signal.epr_curative.count())
        self.assertEqual(2, EPRCurative.objects.count())
