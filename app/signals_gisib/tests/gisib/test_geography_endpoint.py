from rest_framework.test import APITestCase

from signals_gisib.tests.factories import CollectionItemFactory
from signals_gisib.tests.utils import BBOX_AMSTERDAM


class GeographyEndpointTestCase(APITestCase):
    def setUp(self):
        CollectionItemFactory.create_batch(20, object_kind_name='Boom')

    def test_list_geography_filter_object_kind_name_required(self):
        response = self.client.get('/public/gisib/geography/')
        self.assertEqual(response.status_code, 400)

    def test_list_geography_paginated(self):
        for page in range(1, 5):
            response = self.client.get('/public/gisib/geography/', data={'object_kind_name': 'Boom',
                                                                         'page_size': 5, 'page': page})

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['type'], 'FeatureCollection')
            self.assertEqual(len(response.data['features']), 5)

    def test_list_geography_paginated_invalid_page(self):
        response = self.client.get('/public/gisib/geography/', data={'object_kind_name': 'Boom', 'page': 999})
        self.assertEqual(response.status_code, 404)

    def test_list_geography_filtered_by_bbox(self):
        response = self.client.get('/public/gisib/geography/', data={'object_kind_name': 'Boom',
                                                                     'bbox': ','.join(str(x) for x in BBOX_AMSTERDAM)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'FeatureCollection')
        self.assertEqual(len(response.data['features']), 20)

    def test_list_geography_filtered_by_invalid_bbox(self):
        response = self.client.get('/public/gisib/geography/', data={'object_kind_name': 'Boom',
                                                                     'bbox': 'invalid,invalid,invalid,invalid'})
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/public/gisib/geography/',
                                   data={'object_kind_name': 'Boom',
                                         'bbox': f'{",".join(str(x) for x in BBOX_AMSTERDAM)},1.234567890'})
        self.assertEqual(response.status_code, 400)

    def test_list_geography_filtered_by_unknown_object_kind_name(self):
        response = self.client.get('/public/gisib/geography/', data={'object_kind_name': 'object_kind_999'})
        self.assertEqual(response.status_code, 400)
