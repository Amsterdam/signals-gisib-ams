"""
ASGI config for project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

django_application = get_asgi_application()
django_application = OpenTelemetryMiddleware(django_application)


async def application(scope, receive, send):
    """
    Guvicorn doesn't work well with OpenTelemetry without implementing the ASGI middleware to catch requests
    """
    if scope["type"] == "http":
        await django_application(scope, receive, send)
