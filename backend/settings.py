"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
from datetime import timedelta
from envs import env
import os

VERSION = '0.20'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", False, var_type='boolean')


class MissingSecretKey(Exception):
    pass


def raise_debug():
    raise MissingSecretKey


# SECURITY WARNING: keep the secret key used in production secret!
DEV_SECRET_KEY = 'f!e(2rsmnoiyy@+#s$&lg-m7xp3@-+8fveja$plau=ir--13f('

SECRET_KEY = env(
    "DJANGO_SECRET",
    DEBUG and DEV_SECRET_KEY or raise_debug(),
    var_type='string'
)

ALLOWED_HOSTS = []

BACKEND_HOST = env("BACKEND_HOST", '', 'string')
if BACKEND_HOST:
    ALLOWED_HOSTS.append(BACKEND_HOST)


# Auth User
AUTH_USER_MODEL = 'api.User'


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'api.apps.ApiConfig',
    'trumbowyg',
    'location_field.apps.DefaultConfig',
    'anymail',
    'django_inlinecss',
    'django_extensions'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB', '', 'string'),
        'HOST': env('POSTGRES_HOST', '', 'string'),
        'PASSWORD': env('POSTGRES_PASSWORD', '', 'string'),
        'USER': env('POSTGRES_USER', '', 'string'),
        'PORT': os.getenv('POSTGRES_PORT', "5432")
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'static/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONOpenAPIRenderer',
    )
}

ACCESS_TOKEN_LIFETIME = env('ACCESS_TOKEN_LIFETIME', 1, 'integer')
REFRESH_TOKEN_LIFETIME = env('REFRESH_TOKEN_LIFETIME', 7, 'integer')

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=ACCESS_TOKEN_LIFETIME),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=REFRESH_TOKEN_LIFETIME),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

MEDIA_ROOT = 'media/'
MEDIA_URL = 'media/'


# EMAIL CONFIG
ACTIVATION_URL = 'activate/{token}/'
EMAIL_BACKEND = env(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend',
    var_type='string'
)

MG_API_KEY = os.getenv('MG_SENDING_KEY', '')
MG_TRACKING_KEY = os.getenv('MG_TRACKING_KEY') or MG_API_KEY
MG_SENDER_DOMAIN = os.getenv('MG_SENDER_DOMAIN', '')
MG_API_URL = os.getenv('MG_API_URL') or "https://api.mailgun.net/v3"
MG_AMEBA_DOMAIN = os.getenv('MG_AMEBA_DOMAIN') or 'mail-out.ameba.cat'

ANYMAIL = {
    "MAILGUN_API_KEY": MG_API_KEY,
    "MAILGUN_SENDER_DOMAIN": MG_SENDER_DOMAIN,
    "MAILGUN_API_URL": MG_API_URL
}


DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", 'noreply@ameba.cat', 'string')
SERVER_EMAIL = env("SERVER_EMAIL", 'support@ameba.cat')

EMAIL_HOST = env("EMAIL_HOST", '', var_type='string')
EMAIL_HOST_USER = env("EMAIL_HOST_USER", '', var_type='string')
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", '', var_type='string')
EMAIL_PORT = int(os.getenv("EMAIL_PORT") or 465)
EMAIL_USE_SSL = bool(os.getenv("EMAIL_USE_SSL", "").lower() == 'true')
PROFILE_VERSION = 8


STRIPE_SECRET = env("STRIPE_SECRET", '', var_type='string')
STRIPE_PUBLIC = env("STRIPE_PUBLIC", '', var_type='string')


# TOKENS EXPIRE TIMES
ACTIVATION_EXPIRE_DAYS = 30
ACTIVATION_SALT = 'aCtiV4TiONtoKeN'

RECOVERY_EXPIRE_DAYS = .5
RECOVERY_SALT = 'rEc0VErit0kn'


# MAILING LISTS
DEFAULT_MAILING_LIST = env(
    'DEFAULT_MAILING_LIST',
    'newsletter@mail-out.ameba.cat',
    var_type='string'
)


STAFF_DOMAINS = ['jaguarintheloop.live', 'ameba.cat']
TEST_MAILING_LIST_PREFIXES = ['test', 'dev', 'stag', 'sand', 'debug', 'local']
TEST_TEMPLATE = 'unsubscribe.test'
