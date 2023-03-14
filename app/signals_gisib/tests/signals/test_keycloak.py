from unittest.mock import patch

from django.test import TestCase, override_settings

from signals_gisib.signals.keycloak import get_bearer_token


@override_settings(KEYCLOAK_ENABLED=True,
                   KEYCLOAK_SERVER_URL='https://test.com/auth/',
                   KEYCLOAK_CLIENT_ID='test-client-id',
                   KEYCLOAK_REALM_NAME='test-realm',
                   KEYCLOAK_CLIENT_SECRET_KEY='00000000-0000-0000-0000-000000000000',
                   KEYCLOAK_GRANT_TYPE='client_credentials')
class KeycloakApiTestCase(TestCase):
    @patch('signals_gisib.signals.keycloak.KeycloakOpenID.token')
    def test_get_bearer_token(self, mock_token):
        # set the return value of the mocked function
        mock_token.return_value = {'token_type': 'Bearer', 'access_token': 'abcdefg'}

        # call the get_bearer_token function
        token = get_bearer_token()

        # check the return value
        self.assertEqual(token, 'Bearer abcdefg')

    @override_settings(KEYCLOAK_ENABLED=False)
    def test_get_bearer_token_keycloak_disabled(self):
        self.assertIsNone(get_bearer_token())
