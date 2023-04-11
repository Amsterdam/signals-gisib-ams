from django.test import TestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time

from signals_gisib.signals.signal_status_utils import (
    _signal_update_status,
    signal_done_external,
    signal_ready_to_send,
    signal_sent
)
from signals_gisib.tests.factories import EPRCurativeFactory, SignalFactory
from signals_gisib.tests.signals import signals_api_vcr


@freeze_time('2023-04-05T16:00:00+00:00')
@override_settings(SIGNALS_BASE_URI='http://test.com/signals')
class SignalStatusUtilsTestCase(TestCase):
    @signals_api_vcr.use_cassette()
    def test_signal_done_external(self):
        signal = SignalFactory.create(signal_id=1)
        signal_done_external(signal=signal)

    def test_signal_done_external_signal_already_processed(self):
        signal = SignalFactory.create(signal_id=1, processed_at=timezone.now())
        signal_done_external(signal=signal)

    @signals_api_vcr.use_cassette()
    def test_signal_ready_to_send(self):
        signal = SignalFactory.create(signal_id=3)
        signal_ready_to_send(signal=signal)

    def test_signal_ready_to_send_signal_already_processed(self):
        signal = SignalFactory.create(signal_id=3, processed_at=timezone.now())
        signal_ready_to_send(signal=signal)

    @signals_api_vcr.use_cassette()
    def test_signal_sent(self):
        signal = SignalFactory.create(signal_id=3)
        EPRCurativeFactory.create(signal=signal)

        signal_sent(signal=signal)

    def test_signal_sent_signal_already_processed(self):
        signal = SignalFactory.create(signal_id=1, processed_at=timezone.now())
        EPRCurativeFactory.create(signal=signal, processed=True)

        signal_sent(signal=signal)

    @signals_api_vcr.use_cassette()
    def test__signal_update_status_exception(self):
        signal = SignalFactory.create(signal_id=1)
        state = 'sent'
        text = 'test'

        _signal_update_status(signal=signal, state=state, text=text)
