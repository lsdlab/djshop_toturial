from ..base import *

import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "ys7!se3a7$0q$0yy6b$2vq1247u$fnw-(%g(=2+^^t3ol@8!^f"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS += ['drf_yasg']

MIDDLEWARE += ['apps.core.middleware.BetterExceptionsMiddleware']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'localhost',
        'PORT': 5432,
        'NAME': 'djshop_development',
        'USER': 'djshop_development',
        'PASSWORD': 'Ae2V6v7FzrR9UWyANQJR'
    }
}

# django-restframework/jwt/swagger settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES':
    ('rest_framework.permissions.IsAuthenticated', ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.core.csrf_exempt_authentication.CsrfExemptSessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer', ),
    'DATETIME_FORMAT':
    "%Y-%m-%d %H:%M:%S",
    'DEFAULT_PAGINATION_CLASS':
    'apps.core.pagination.StandardResultsSetPagination',
}

SWAGGER_SETTINGS = {
    'LOGIN_URL': '/admin/logout',
    'LOGOUT_URL': '/admin/logout',
}

SHELL_PLUS = 'ipython'

# celery settings
BROKER_URL = 'amqp://djshop:Ae2V6v7FzrR9UWyANQJR@localhost:5672/%2F'
# BROKER_URL = 'redis://root:50f84daf3a6dfd6a9f20@localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://root:Ae2V6v7FzrR9UWyANQJR@localhost:6379/2'

# django-redis settings
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": 'redis://root:Ae2V6v7FzrR9UWyANQJR@localhost:6379/3',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
