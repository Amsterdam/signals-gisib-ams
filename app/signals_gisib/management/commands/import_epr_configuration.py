from django.core.management.base import BaseCommand

from signals_gisib.gisib.import_epr_configuration import start_import


class Command(BaseCommand):
    help = 'Start import of EPR configuration needed to translate between Signals and GISIB'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', dest='clear', default=False,
                            help='Clear the configuration from the table before starting the import.')

    def handle(self, *args, **options):
        clear = options['clear']

        start_import(clear_table=clear)
        self.stdout.write(self.style.SUCCESS('Import completed successfully'))
