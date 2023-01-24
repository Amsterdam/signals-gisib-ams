from django.test import TestCase

from signals_gisib.tests.factories import CollectionItemFactory


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
