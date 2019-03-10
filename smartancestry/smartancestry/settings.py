"""
Django settings for smartancestry project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import django

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from django.utils.translation import ugettext_lazy as _

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9$+_xwu)k_k7a-_-9-dkpums4jt^r&2qwd0y*&sau+1wbhu_h8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'data.apps.DataConfig',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_PATH, 'template')
        ],
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

ROOT_URLCONF = 'smartancestry.urls'

WSGI_APPLICATION = 'smartancestry.wsgi.application'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose'
        },
        'file2': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose'
        },
        'file_forms': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'forms.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file2'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'data.models': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'data.forms': {
            'handlers': ['file_forms'],
            'level': 'DEBUG',
        },
    }
}

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'de-de'

LANGUAGES = (
    ('de', _('German')),
    ('en', _('English')),
)

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = '/Users/michaelrommel/Prog/SmartAncestry/smartancestry/smartancestry'
MEDIA_ROOT = '/Users/michaelrommel/Prog/SmartAncestry/smartancestry/data'
MEDIA_URL = '/media/'

django.setup()
