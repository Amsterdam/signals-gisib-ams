from rest_framework.test import APITestCase

from signals_gisib.tests.factories import CollectionItemFactory
from signals_gisib.tests.utils import BBOX_AMSTERDAM


class GeographyEndpointTestCase(APITestCase):
    def setUp(self):
        CollectionItemFactory.create_batch(5, object_kind_name='object_kind_1')
        CollectionItemFactory.create_batch(5, object_kind_name='object_kind_2')
        CollectionItemFactory.create_batch(5, object_kind_name='object_kind_3')
        CollectionItemFactory.create_batch(5, object_kind_name='object_kind_4')

    def test_list_geography(self):
        response = self.client.get('/public/gisib/geography/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'FeatureCollection')
        self.assertEqual(len(response.data['features']), 20)

    def test_list_geography_paginated(self):
        for page in range(1, 5):
            response = self.client.get('/public/gisib/geography/', data={'page_size': 5, 'page': page})

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['type'], 'FeatureCollection')
            self.assertEqual(len(response.data['features']), 5)

    def test_list_geography_paginated_invalid_page(self):
        response = self.client.get('/public/gisib/geography/', data={'page': 999})
        self.assertEqual(response.status_code, 404)

    def test_list_geography_filtered_by_object_kind_name(self):
        response = self.client.get('/public/gisib/geography/', data={'object_kind_name': 'object_kind_2'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'FeatureCollection')
        self.assertEqual(len(response.data['features']), 5)

    def test_list_geography_filtered_by_bbox(self):
        response = self.client.get('/public/gisib/geography/', data={'bbox': ','.join(str(x) for x in BBOX_AMSTERDAM)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'FeatureCollection')
        self.assertEqual(len(response.data['features']), 20)

    def test_list_geography_filtered_by_invalid_bbox(self):
        response = self.client.get('/public/gisib/geography/', data={'bbox': 'invalid,invalid,invalid,invalid'})
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/public/gisib/geography/',
                                   data={'bbox': f'{",".join(str(x) for x in BBOX_AMSTERDAM)},1.234567890'})
        self.assertEqual(response.status_code, 400)

    def test_list_geography_filtered_by_unknown_object_kind_name(self):
        response = self.client.get('/public/gisib/geography/', data={'object_kind_name': 'object_kind_999'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'FeatureCollection')
        self.assertEqual(len(response.data['features']), 0)
