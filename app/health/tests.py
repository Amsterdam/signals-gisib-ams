from rest_framework.test import APITestCase


class HealthCheckTestCase(APITestCase):
    def test_health_check(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'OK')
