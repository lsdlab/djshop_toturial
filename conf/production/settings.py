from ..base import *

import os


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': '',
        'PORT': 5432,
        'NAME': 'djshop_production',
        'USER': 'djseriers',
        'PASSWORD': ''
    }
}

# django-restframework/jwt
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES':
    ('rest_framework.permissions.IsAuthenticated', ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.core.csrf_exempt_authentication.CsrfExemptSessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer', ),
    'DATETIME_FORMAT':
    "%Y-%m-%d %H:%M:%S",
    'DEFAULT_PAGINATION_CLASS':
    'apps.core.pagination.StandardResultsSetPagination',
}

# celery settings
BROKER_URL = 'amqp://djshop:@localhost:5672/%2F'
# BROKER_URL = 'redis://root:@localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://root:@localhost:6379/2'

# django-redis settings
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": 'redis://root:@localhost:6379/3',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
