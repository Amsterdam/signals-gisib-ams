from unittest.mock import patch

from django.test import TransactionTestCase, override_settings
from freezegun import freeze_time

from signals_gisib.gisib.epr_curative_status import check_status
from signals_gisib.tests.factories import CollectionItemFactory, EPRCurativeFactory, SignalFactory


@freeze_time('2023-02-08T08:50:00+00:00')
@override_settings(GISIB_BASE_URI='https://amsterdam-test.gisib.nl/api/api', GISIB_USERNAME='test-user',
                   GISIB_PASSWORD='test-password', GISIB_APIKEY='test-api-key')
class EPRCurativeStatusTestCase(TransactionTestCase):
    def setUp(self):
        self.collection_items = []
        for status in ['a. Melding', 'b. Inspecteren', 'c. Registratie EPR', 'd. Geen', 'e. EPR niet bestrijden',
                       'f. EPR Bestreden', 'g. EPR Deels bestreden', 'i. Niet in beheergebied EPR Gemeente Amsterdam']:
            colleciont_item = CollectionItemFactory.create(object_kind_name='Registratie EPR',
                                                           raw_properties={'Description': status},
                                                           geometry=None)
            self.collection_items.append(colleciont_item)

    @patch('signals_gisib.gisib.epr_curative_status.update_epr_curatives_for_signal')
    def test_check_status(self, update_epr_curatives_for_signal_mock):
        test_signal = SignalFactory.create()

        update_epr_curatives_for_signal_mock.return_value = (test_signal, True,)

    def test_check_status_not_in_epr_flow(self):
        test_signal = SignalFactory.create()
        test_signal.flow = 'NOT-THE-CORRECT-FLOW'

        check_status(signal=test_signal)

    @patch('signals_gisib.gisib.epr_curative_status.update_epr_curatives_for_signal')
    def test_status_partially_processed(self, update_epr_curatives_for_signal_mock):
        test_signal = SignalFactory.create()

        inspecteren_properties = {
            'Registratie EPR': {
                'Id': self.collection_items[1].gisib_id,
                'Description': self.collection_items[1].raw_properties['Description']
            }
        }
        EPRCurativeFactory.create(signal=test_signal, processed=False,
                                  status_id=self.collection_items[1].gisib_id,
                                  collection_item__raw_properties=inspecteren_properties)

        bestreden_properties = {
            'Registratie EPR': {
                'Id': self.collection_items[5].gisib_id,
                'Description': self.collection_items[5].raw_properties['Description']
            }
        }
        EPRCurativeFactory.create(signal=test_signal, processed=False,
                                  collection_item__raw_properties=bestreden_properties)

        update_epr_curatives_for_signal_mock.return_value = (test_signal, True,)

        self.assertIsNone(test_signal.processed_at)

        check_status(signal=test_signal)

        test_signal.refresh_from_db()
        self.assertIsNone(test_signal.processed_at)

    @patch('signals_gisib.gisib.epr_curative_status.update_epr_curatives_for_signal')
    def test_status_no_updates(self, update_epr_curatives_for_signal_mock):
        test_signal = SignalFactory.create()
        EPRCurativeFactory.create(signal=test_signal, processed=False)

        update_epr_curatives_for_signal_mock.return_value = (test_signal, False, )

        self.assertIsNone(test_signal.processed_at)

        check_status(signal=test_signal)

        test_signal.refresh_from_db()
        self.assertIsNone(test_signal.processed_at)

    @patch('signals_gisib.gisib.epr_curative_status.update_epr_curatives_for_signal')
    def test_status_no_unprocessed_epr_curatives(self, update_epr_curatives_for_signal_mock):
        test_signal = SignalFactory.create()
        EPRCurativeFactory.create(signal=test_signal, processed=True)

        update_epr_curatives_for_signal_mock.return_value = (test_signal, True,)

        self.assertIsNone(test_signal.processed_at)

        check_status(signal=test_signal)

        test_signal.refresh_from_db()
        self.assertIsNone(test_signal.processed_at)
