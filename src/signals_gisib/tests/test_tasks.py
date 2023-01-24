from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase

from signals_gisib.tasks import import_quercus_trees


class ImportQuercusTreesTest(TestCase):
    @patch('signals_gisib.tasks.start_import')
    def test_import_quercus_trees(self, start_import_mock):
        # Call the import_quercus_trees function
        import_quercus_trees()

        # Assert that the start_import function was called
        start_import_mock.assert_called_once()

        # Assert that the start_import function was called with the default arguments
        start_import_mock.assert_called_with(time_delta=None, clear_table=False)

    @patch('signals_gisib.tasks.start_import')
    def test_import_quercus_trees_with_args(self, start_import_mock):
        # Call the import_quercus_trees function with custom arguments
        time_delta = timedelta(days=7)
        import_quercus_trees(time_delta=time_delta, clear_table=True)

        # Assert that the start_import function was called
        start_import_mock.assert_called_once()

        # Assert that the start_import function was called with the custom arguments
        start_import_mock.assert_called_with(time_delta=time_delta, clear_table=True)
