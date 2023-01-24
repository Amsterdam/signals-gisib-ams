from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class ImportOakTreesCommandTest(TestCase):
    @patch('signals_gisib.management.commands.import_oak_trees.start_import')
    def test_handle_command(self, start_import_mock):
        # Call the import oak trees management command
        call_command('import_oak_trees')

        # Assert that the start_import function was called
        start_import_mock.assert_called_once()

        # Assert that the start_import function was called with the default arguments
        start_import_mock.assert_called_with(time_delta=None, clear_table=False)

    @patch('signals_gisib.management.commands.import_oak_trees.start_import')
    def test_handle_command_with_args(self, start_import_mock):
        # Call the import oak trees management command with custom arguments
        call_command('import_oak_trees', '--days=7', '--clear')

        # Assert that the start_import function was called
        start_import_mock.assert_called_once()

        # Assert that the start_import function was called with the custom arguments
        start_import_mock.assert_called_with(time_delta=timedelta(days=7), clear_table=True)

    def test_handle_command_with_negative_days(self):
        # Call the import oak trees management command with negative days
        buffer = StringIO()
        call_command('import_oak_trees', '--days=-7', stderr=buffer)

        output = buffer.getvalue()
        self.assertIn('days must be a positive integer', output)
