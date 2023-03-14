import copy

from django.test import TransactionTestCase, override_settings
from django.utils import timezone
from freezegun import freeze_time

from signals_gisib.gisib.create_epr_curative import (
    _create_post_collection_insert_body,
    _get_tree_ids,
    _translate_nest_size,
    _tree_exists,
    create_epr_curative
)
from signals_gisib.models import EPRCurative
from signals_gisib.tests.factories import CollectionItemFactory, SignalFactory
from signals_gisib.tests.fuzzy import FuzzyPoint
from signals_gisib.tests.gisib import gisib_api_vcr
from signals_gisib.tests.utils import BBOX_AMSTERDAM


@freeze_time('2023-01-24T08:50:00+00:00')
@override_settings(GISIB_ENDPOINT='https://amsterdam-test.gisib.nl/api/api', GISIB_USERNAME='test-user',
                   GISIB_PASSWORD='test-password', GISIB_APIKEY='test-api-key')
class CreateEPRCurativeTestCase(TransactionTestCase):
    def setUp(self):
        CollectionItemFactory.create(gisib_id=920107, object_kind_name='Boom',
                                     properties={'species': 'Quercus robur'},
                                     raw_properties={'Id': 123456789, 'Soortnaam': {'Description': 'Quercus robur'}})
        CollectionItemFactory.create(gisib_id=3749026, object_kind_name='Nestformaat',
                                     raw_properties={'Id': 3749026,
                                                     'Description': 'Rupsen bedekken de stam als een deken'})

    def test__tree_exists(self):
        self.assertTrue(_tree_exists(920107))
        self.assertFalse(_tree_exists(999))

    def test__get_tree_ids(self):
        extra_properties = [{'id': 'extra_eikenprocessierups',
                             'answer': [{'type': 'Niet op de kaart'},
                                        {'id': 920107, 'type': 'Eikenboom'},
                                        {'type': 'Niet op de kaart'},
                                        ]}, {'id': 'extra_nest_grootte',
                                             'label': 'Op de boom gezien',
                                             'answer': {'id': 'deken',
                                                        'label': 'Rupsen bedekken de stam als een deken'}}]

        tree_ids = _get_tree_ids(extra_properties)

        self.assertEqual(len(tree_ids), 2)
        self.assertIn(None, tree_ids)
        self.assertIn(920107, tree_ids)

    def test__translate_nest_size(self):
        extra_properties = [{'id': 'extra_eikenprocessierups',
                             'answer': [{'id': 920107, 'type': 'Eikenboom'},
                                        {'type': 'Niet op de kaart'},
                                        ]}, {'id': 'extra_nest_grootte',
                                             'label': 'Op de boom gezien',
                                             'answer': {'id': 'deken',
                                                        'label': 'Rupsen bedekken de stam als een deken'}}]

        self.assertEqual(_translate_nest_size(extra_properties), 3749026)

        extra_properties = []
        self.assertIsNone(_translate_nest_size(extra_properties))

        extra_properties = [{'id': 'extra_nest_grootte', 'label': 'Op de boom gezien',
                             'answer': {'id': 'voetbal', 'label': 'Nest is zo groot als een voetbal'}}]
        self.assertIsNone(_translate_nest_size(extra_properties))

    def test__create_post_collection_insert_body(self):
        now = timezone.now()
        fuzzy_point = FuzzyPoint(*BBOX_AMSTERDAM)
        point = fuzzy_point.fuzz()
        point_28992 = copy.deepcopy(point)
        point_28992.transform(28992)

        body = _create_post_collection_insert_body(signal_id=123, signal_created_at=now, signal_geometry=point,
                                                   nest_size=920107, tree_id=920107)

        self.assertEqual(body['ObjectKindNaam'], 'EPR Curatief')
        self.assertEqual(body['Properties']['SIG Nummer melding'], 123)
        self.assertEqual(body['Properties']['Datum melding'], now.strftime('%d-%m-%Y %H:%M'))
        self.assertEqual(body['Properties']['Nestformaat'], 920107)
        self.assertEqual(body['Properties']['Boom'], 920107)
        self.assertNotIn('Geometry', body)

        body = _create_post_collection_insert_body(signal_id=123, signal_created_at=now, signal_geometry=point,
                                                   nest_size=920107, tree_id=None)

        self.assertEqual(body['ObjectKindNaam'], 'EPR Curatief')
        self.assertEqual(body['Properties']['SIG Nummer melding'], 123)
        self.assertEqual(body['Properties']['Datum melding'], now.strftime('%d-%m-%Y %H:%M'))
        self.assertEqual(body['Properties']['Nestformaat'], 920107)
        self.assertNotIn('Boom', body['Properties'])
        self.assertEqual(body['Geometry']['type'], 'Point')
        self.assertEqual(body['Geometry']['coordinates'][0], point_28992.coords[0])
        self.assertEqual(body['Geometry']['coordinates'][1], point_28992.coords[1])

    @gisib_api_vcr.use_cassette()
    def test_create_epr_curative(self):
        signal = SignalFactory.create(
            signal_id=123456,
            signal_extra_properties=[{'id': 'extra_eikenprocessierups',
                                      'answer': [{'type': 'Niet op de kaart'},
                                                 {'id': 920107, 'type': 'Eikenboom'},
                                                 {'type': 'Niet op de kaart'},
                                                 ]}, {'id': 'extra_nest_grootte',
                                                      'label': 'Op de boom gezien',
                                                      'answer': {'id': 'deken',
                                                                 'label': 'Rupsen bedekken de stam als een deken'}}])

        self.assertEqual(EPRCurative.objects.count(), 0)

        created_epr_curative_ids = create_epr_curative(signal=signal)

        self.assertEqual(len(created_epr_curative_ids), 2)
        self.assertEqual(EPRCurative.objects.count(), 2)
