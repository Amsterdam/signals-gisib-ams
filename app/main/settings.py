"""
Django settings for the project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from typing import Any

# Export modules to Azure Application Insights
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter, AzureMonitorTraceExporter
# Opentelemetry modules needed for logging and tracing
from opentelemetry import trace
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


TRUE_VALUES = [True, 'True', 'true', '1']

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'insecure')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', False) in TRUE_VALUES
LOGGING_LEVEL: str = os.getenv('LOGGING_LEVEL', 'INFO')

AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING = os.getenv('AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING', None)

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,0.0.0.0,localhost').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django_celery_beat',
    'django_celery_results',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'django_extensions',
    'rest_framework',
    'drf_yasg',
    'simple_history',
    'corsheaders',
    'signals_gisib',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#caches

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'signals-gisib'),
        'USER': os.getenv('DATABASE_USER', 'signals-gisib'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': os.getenv('DATABASE_HOST', '127.0.0.1'),
        'PORT': os.getenv('DATABASE_PORT', 54321)
    },
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Security settings
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', False) in TRUE_VALUES
SECURE_REDIRECT_EXEMPT = [r'^health/', ]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', False) in TRUE_VALUES
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', False) in TRUE_VALUES


# Debug toolbar
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar', ]
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
    INTERNAL_IPS = ['127.0.0.1', '0.0.0.0', ]


# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': int(os.getenv('REST_FRAMEWORK_PAGE_SIZE', '100')),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}


# Celery
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'signals-gisib-ams')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'insecure')
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', 'vhost')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = os.getenv('RABBITMQ_PORT', 5672)

CELERY_BROKER_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_EXTENDED = True
CELERY_TASK_RESULT_EXPIRES = 604800  # 7 days in seconds (7*24*60*60)
CELERY_TASK_ALWAYS_EAGER = os.getenv('CELERY_TASK_ALWAYS_EAGER', False)


# Celery Beat settings
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BEAT_SCHEDULE = {}


# GISIB Setting
GISIB_BASE_URI = os.getenv('GISIB_BASE_URI')
GISIB_USERNAME = os.getenv('GISIB_USERNAME')
GISIB_PASSWORD = os.getenv('GISIB_PASSWORD')
GISIB_APIKEY = os.getenv('GISIB_APIKEY')
GISIB_LIMIT = int(os.getenv('GISIB_LIMIT', '500'))
GISIB_SLEEP = float(os.getenv('GISIB_SLEEP', '0.5'))  # seconds to sleep between consecutive calls
GISIB_REGISTRATIE_EPR_NOT_PROCESSED_STATUSES = os.getenv(
    'GISIB_REGISTRATIE_EPR_NOT_PROCESSED_STATUSES',
    'a. Melding,b. Inspectie,c. Registratie EPR,g. EPR Deels bestreden'
).split(',')
GISIB_REGISTRATIE_EPR_PROCESSED_STATUSES = os.getenv(
    'GISIB_REGISTRATIE_EPR_PROCESSED_STATUSES',
    'd. Geen,e. EPR Niet bestrijden,f. EPR Bestreden,h. Dubbele melding,i. Niet in beheergebied'
).split(',')
GISIB_REGISTRATIE_EPR_STATUSES = GISIB_REGISTRATIE_EPR_NOT_PROCESSED_STATUSES + GISIB_REGISTRATIE_EPR_PROCESSED_STATUSES


# Keycloak (Used to get tokens for the Signals API)
KEYCLOAK_ENABLED = os.getenv('KEYCLOAK_ENABLED', False)
KEYCLOAK_SERVER_URL = os.getenv('KEYCLOAK_SERVER_URL')
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID')
KEYCLOAK_REALM_NAME = os.getenv('KEYCLOAK_REALM_NAME')
KEYCLOAK_CLIENT_SECRET_KEY = os.getenv('KEYCLOAK_CLIENT_SECRET_KEY')
KEYCLOAK_GRANT_TYPE = os.getenv('KEYCLOAK_GRANT_TYPE')


# Signals API
SIGNALS_BASE_URI = os.getenv('SIGNALS_BASE_URI')


# CORS
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', False) in TRUE_VALUES
CORS_ALLOWED_ORIGINS = [origin.strip()
                        for origin in os.getenv('CORS_ALLOWED_ORIGINS', 'null').split(',')]
CORS_EXPOSE_HEADERS = [
    'Link',  # Added for the geography endpoint
]
CORS_ALLOW_CREDENTIALS = True


# Per default log to console
LOGGING_HANDLERS: dict[str, dict[str, Any]] = {
    'console': {
        'class': 'logging.StreamHandler',
    },
}
LOGGER_HANDLERS = ['console', ]

MONITOR_SERVICE_NAME = 'gisib-signals'
resource: Resource = Resource.create({"service.name": MONITOR_SERVICE_NAME})

tracer_provider: TracerProvider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)


# As required, the user id and name is attached to each request that is recorded as a span
def response_hook(span, request, response):
    if span and span.is_recording() and request.user.is_authenticated:
        span.set_attribute('user_id', request.user.id)
        span.set_attribute('username', request.user.username)


# Logs and traces will be exported to Azure Application Insights
if AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING:

    # Enable exporting of traces
    span_exporter: AzureMonitorTraceExporter = AzureMonitorTraceExporter(
        connection_string=AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING
    )
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter=span_exporter))

    # Enable exporting of logs
    log_exporter: AzureMonitorLogExporter = AzureMonitorLogExporter(
        connection_string=AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING
    )
    logger_provider: LoggerProvider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter, schedule_delay_millis=3000))

    # Custom logging handler to attach to logging config
    class AzureLoggingHandler(LoggingHandler):
        def __init__(self):
            super().__init__(logger_provider=logger_provider)

    LOGGING_HANDLERS.update({
        'azure': {
            '()': AzureLoggingHandler,
        }
    })

    LOGGER_HANDLERS.append('azure')

# Instrument the postgres database
# This will attach logs from the logger module to traces
Psycopg2Instrumentor().instrument(tracer_provider=tracer_provider, skip_dep_check=True)
DjangoInstrumentor().instrument(tracer_provider=tracer_provider, response_hook=response_hook)

LOGGING: dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'elaborate': {
            'format': '{levelname} {module}.{filename} {message}',
            'style': '{'
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': LOGGING_HANDLERS,
    'loggers': {
        '': {
            'level': LOGGING_LEVEL,
            'handlers': LOGGER_HANDLERS,
            'propagate': False,
        },
        'django.utils.autoreload': {
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

if AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING:
    LOGGING['loggers'].update({
        "azure.monitor.opentelemetry.exporter.export._base": {
            "handlers": LOGGER_HANDLERS,
            "level": "ERROR",  # Set to INFO to log what is being logged to Azure
        },
        "azure.core.pipeline.policies.http_logging_policy": {
            "handlers": LOGGER_HANDLERS,
            "level": "ERROR",  # Set to INFO to log what is being logged to Azure
        },
    })
else:
    # When in debug mode without Azure Insights, queries will be logged to console
    LOGGING['loggers'].update({
        'django.db.backends': {
            'handlers': LOGGER_HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
            'filters': ['require_debug_true', ],
        }
    })

# Swagger

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': None,
    'USE_SESSION_AUTH': False,
}
