#!/usr/bin/env python

import django
import json
import os
import sys

from django.conf import settings
from django.core.management import execute_from_command_line


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DDM_DIR = os.path.join(PROJECT_DIR, 'ddm')
VUE_FRONTEND_DIR = os.path.join(PROJECT_DIR, 'vue_frontend')

sys.path.append(PROJECT_DIR)
sys.path.append(DDM_DIR)

# Import local test settings.
test_config = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_config.json')))

# Define Database Configuration.

if os.environ.get('DB') in ['mysql', 'postgres']:
    DB_CONFIG = {
        'default': {
            'ENGINE': os.environ.get('DB_ENGINE'),
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': '127.0.0.1',
            'PORT': os.environ.get('DB_PORT')
        }
    }
else:
    DB_CONFIG = {
        'default': {
            'ENGINE': test_config['DB_ENGINE'],
            'NAME': test_config['DB_NAME'],
        }
    }


# Initialize Settings.
settings.configure(
    INSTALLED_APPS=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.sites',
        'django.contrib.staticfiles',
        'ddm.apps.DdmConfig',
        'ckeditor',
        'webpack_loader',
        'rest_framework',
        'rest_framework.authtoken',
    ],
    MIDDLEWARE=[
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.contrib.sites.middleware.CurrentSiteMiddleware',
    ],
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['templates'],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                ],
            },
        },
    ],
    ALLOWED_HOSTS=['localhost', '127.0.0.1'],
    ROOT_URLCONF='urls',
    DATABASES=DB_CONFIG,
    DEBUG=True,
    SECRET_KEY=test_config['SECRET_KEY'],
    SITE_ID=1,
    STATIC_URL='/static/',
    USE_TZ=True,
    STATICFILES_DIRS=(
        os.path.join(DDM_DIR, 'static'),
    ),
    WEBPACK_LOADER={
        'DEFAULT': {
            # 'CACHE': not settings.DEBUG,
            'BUNDLE_DIR_NAME': 'ddm/vue/',
            'STATS_FILE': os.path.join(DDM_DIR, 'static', 'ddm', 'vue', 'webpack-stats.json'),
            'POLL_INTERVAL': 0.1,
            'TIMEOUT': None,
            'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
        }
    },
    DDM_SETTINGS={
        'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)uzh\.ch$',
    },
    AUTH_PASSWORD_VALIDATORS=[
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
    ]
)

django.setup()

execute_from_command_line(sys.argv)
