from datetime import timedelta

from django.test import TransactionTestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time

from signals_gisib.gisib.update_epr_curative import update_epr_curatives_for_signal
from signals_gisib.tests.factories import CollectionItemFactory, EPRCurativeFactory, SignalFactory
from signals_gisib.tests.gisib import gisib_api_vcr


@freeze_time('2023-03-01T15:00:00+00:00')
@override_settings(GISIB_BASE_URI='https://amsterdam-test.gisib.nl/api/api', GISIB_USERNAME='test-user',
                   GISIB_PASSWORD='test-password', GISIB_APIKEY='test-api-key')
class UpdateEPRCurativeTestCase(TransactionTestCase):
    @gisib_api_vcr.use_cassette()
    def test_update_epr_curatives_for_signal_first_check(self):
        tree = CollectionItemFactory.create(object_kind_name='Boom', gisib_id=1879642,
                                            properties={'species': 'Quercus'})
        signal_extra_properties = [{'id': 'extra_eikenprocessierups',
                                    'answer': [{'id': tree.gisib_id,
                                                'type': 'Eikenboom'}, ]},
                                   {'id': 'extra_nest_grootte',
                                    'label': 'Op de boom gezien',
                                    'answer': {'id': 'deken',
                                               'label': 'Rupsen bedekken de stam als een deken'}}]
        epr_curative = EPRCurativeFactory.create(signal__signal_extra_properties=signal_extra_properties,
                                                 collection_item=None, gisib_id=3751039)

        _, updated = update_epr_curatives_for_signal(epr_curative.signal)

        epr_curative.refresh_from_db()

        self.assertTrue(updated)
        self.assertIsNotNone(epr_curative.collection_item)

    @gisib_api_vcr.use_cassette()
    def test_update_epr_curatives_for_signal(self):
        tree = CollectionItemFactory.create(object_kind_name='Boom', gisib_id=1879642,
                                            properties={'species': 'Quercus'})
        signal_extra_properties = [{'id': 'extra_eikenprocessierups',
                                    'answer': [{'id': tree.gisib_id,
                                                'type': 'Eikenboom'}, ]},
                                   {'id': 'extra_nest_grootte',
                                    'label': 'Op de boom gezien',
                                    'answer': {'id': 'deken',
                                               'label': 'Rupsen bedekken de stam als een deken'}}]
        yesterday = timezone.now() - timedelta(weeks=1)
        collection_item = CollectionItemFactory.create(object_kind_name='EPR Curatief', gisib_id=3751039,
                                                       raw_properties={'LastUpdate': yesterday.isoformat()})
        epr_curative = EPRCurativeFactory.create(signal__signal_extra_properties=signal_extra_properties,
                                                 collection_item=collection_item, gisib_id=3751039)

        _, updated = update_epr_curatives_for_signal(epr_curative.signal)

        epr_curative.refresh_from_db()

        self.assertTrue(updated)
        self.assertIsNotNone(epr_curative.collection_item)

    @gisib_api_vcr.use_cassette()
    def test_update_epr_curatives_for_signal_no_updates(self):
        tree = CollectionItemFactory.create(object_kind_name='Boom', gisib_id=1879642,
                                            properties={'species': 'Quercus'})
        signal_extra_properties = [{'id': 'extra_eikenprocessierups',
                                    'answer': [{'id': tree.gisib_id,
                                                'type': 'Eikenboom'}, ]},
                                   {'id': 'extra_nest_grootte',
                                    'label': 'Op de boom gezien',
                                    'answer': {'id': 'deken',
                                               'label': 'Rupsen bedekken de stam als een deken'}}]
        yesterday = timezone.now() - timedelta(weeks=1)
        collection_item = CollectionItemFactory.create(object_kind_name='EPR Curatief', gisib_id=3751039,
                                                       raw_properties={'LastUpdate': yesterday.isoformat()})
        epr_curative = EPRCurativeFactory.create(signal__signal_extra_properties=signal_extra_properties,
                                                 collection_item=collection_item, gisib_id=3751039)

        _, updated = update_epr_curatives_for_signal(epr_curative.signal)
        self.assertFalse(updated)

    def test_update_epr_curatives_for_signal_no_ep_curatives(self):
        signal = SignalFactory.create()

        updated_signal, updated = update_epr_curatives_for_signal(signal)
        self.assertEqual(signal.signal_id, updated_signal.signal_id)
        self.assertFalse(updated)
