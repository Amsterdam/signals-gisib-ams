from django.test import TestCase

from signals_gisib.tests.factories import CollectionItemFactory, EPRCurativeFactory


class CollectionItemTestCase(TestCase):
    def setUp(self):
        self.item1 = CollectionItemFactory.create(
            gisib_id=1, object_kind_name='test_item', properties={'test': 'item'},
            raw_properties={'test': 'item', 'id': '1'}
        )
        self.item2 = CollectionItemFactory.create(
            gisib_id=2, object_kind_name='test_item', properties={'test': 'item'},
            raw_properties={'test': 'item', 'id': '2'}
        )
        self.item3 = CollectionItemFactory.create(
            gisib_id=3, object_kind_name='test_item', properties={'test': 'item'},
            raw_properties={'test': 'item', 'id': '3'}
        )

    def test_str_representation(self):
        self.assertEqual(str(self.item1), '1')
        self.assertEqual(str(self.item2), '2')
        self.assertEqual(str(self.item3), '3')


class EPRCurativeTestCase(TestCase):
    def setUp(self):
        self.epr_status = CollectionItemFactory.create(gisib_id=1,
                                                       object_kind_name='Registratie EPR',
                                                       properties={'Description': 'Test status'},
                                                       raw_properties={'Description': 'Test status'})
        self.epr_curative_1 = EPRCurativeFactory.create(gisib_id=1000, status_id=1)
        self.epr_curative_2 = EPRCurativeFactory.create(gisib_id=2000, status_id=2)

    def test_str_representation(self):
        self.assertEqual(str(self.epr_curative_1), '1000 (Test status)')
        self.assertEqual(str(self.epr_curative_2), '2000 (unknown)')

    def test_get_status_display(self):
        self.assertEqual(self.epr_curative_1.get_status_display(), 'Test status')
        self.assertEqual(self.epr_curative_2.get_status_display(), 'unknown')
