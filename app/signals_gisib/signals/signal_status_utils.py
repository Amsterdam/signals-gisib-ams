import logging

from requests import HTTPError

from signals_gisib.models import Signal
from signals_gisib.signals.api import patch_v1_private_signal_status

logger = logging.getLogger(__name__)


def _signal_update_status(signal: Signal, state, text):
    try:
        patch_v1_private_signal_status(signal.signal_id, state, text)
    except HTTPError as e:
        logger.error(f'Error updating signal {signal.signal_id}: {e}')
        return


def signal_done_external(signal: Signal):
    """
    Processes the given signal by checking if it has been processed and if all EPR curatives have been processed.
    If the signal has not been processed and all EPR curatives have been processed, the signal status is updated to
    'done' and the signal is marked as processed.

    Args:
       signal (Signal): The Signal object to process.

    Returns:
       None
    """
    # Let's get the latest data of the signal from the database
    signal.refresh_from_db()

    if not signal.processed and not signal.epr_curative.filter(processed=False).exists():
        # Update the signal
        state = 'done external'
        text = 'Alle EPR curatief meldingen zijn afgehandeld.'
        _signal_update_status(signal, state, text)

        signal.processed = True
        signal.save()


def signal_ready_to_send(signal: Signal):
    """
    If the signal has not been processed and no EPR curatives have been created, the signal status is updated to
    'ready to send'.

    Args:
       signal (Signal): The Signal object to process.

    Returns:
       None
    """
    # Let's get the latest data of the signal from the database
    signal.refresh_from_db()

    if not signal.processed and not signal.epr_curative.exists():
        state = 'ready to send'
        text = 'Melding klaar om verzonden te worden naar GISIB'
        _signal_update_status(signal, state, text)


def signal_sent(signal: Signal):
    """
    If the signal has not been processed and EPR curatives have been created, the signal status is updated to 'Sent'.

    Args:
       signal (Signal): The Signal object to process.

    Returns:
       None
    """
    # Let's get the latest data of the signal from the database
    signal.refresh_from_db()

    if not signal.processed and signal.epr_curative.exists():
        _ids = ', '.join([str(_id) for _id in signal.epr_curative.only('gisib_id').values_list('gisib_id', flat=True)])

        state = 'sent'
        text = f'EPR Curatief meldingen aangemaakt in GISIB: {_ids}'
        _signal_update_status(signal, state, text)
