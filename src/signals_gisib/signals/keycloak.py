from typing import Union

from django.conf import settings
from keycloak import KeycloakOpenID


def get_bearer_token() -> Union[str, None]:
    if not settings.KEYCLOAK_ENABLED:
        return

    keycloak_openid = KeycloakOpenID(server_url=settings.KEYCLOAK_SERVER_URL,
                                     client_id=settings.KEYCLOAK_CLIENT_ID,
                                     realm_name=settings.KEYCLOAK_REALM_NAME,
                                     client_secret_key=settings.KEYCLOAK_CLIENT_SECRET_KEY)
    token = keycloak_openid.token(grant_type=settings.KEYCLOAK_GRANT_TYPE)

    return f'{token["token_type"]} {token["access_token"]}'
