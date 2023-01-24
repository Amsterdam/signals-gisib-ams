from datetime import timedelta

from celery import shared_task

from signals_gisib.gisib.import_oak_trees import start_import


@shared_task
def import_quercus_trees(time_delta: timedelta = None, clear_table: bool = False):
    start_import(time_delta=time_delta, clear_table=clear_table)
