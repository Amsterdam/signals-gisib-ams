from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.utils import timezone

from signals_gisib.gisib.import_oak_trees import start_import


class Command(BaseCommand):
    help = 'Start import oak trees data'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=None,
                            help='Number of days in the past to import oak trees')
        parser.add_argument('--clear', action='store_true', dest='clear', default=False,
                            help='Clear the oak trees from the table before starting the import.')

    def handle(self, *args, **options):
        days = options['days']
        clear = options['clear']

        if days:
            try:
                if days <= 0:
                    raise ValidationError('days must be a positive integer')
            except ValidationError as e:
                self.stderr.write(str(e))
                return

        delta = timezone.timedelta(days=days) if days else None
        start_import(time_delta=delta, clear_table=clear)
        self.stdout.write(self.style.SUCCESS('Oak trees import completed successfully'))
