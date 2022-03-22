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

sys.path.append('..')
sys.path.append(PROJECT_DIR)
sys.path.append(DDM_DIR)

# Import local test settings.
test_config = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_config.json')))

settings.configure(
    INSTALLED_APPS=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.sites',
        'django.contrib.staticfiles',
        'sekizai',
        'ddm.apps.DdmConfig',
        'ckeditor',
        'webpack_loader',
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
                    'sekizai.context_processors.sekizai',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                ],
            },
        },
    ],
    SESSION_SAVE_EVERY_REQUEST=True,
    ALLOWED_HOSTS=['localhost', '127.0.0.1'],
    ROOT_URLCONF='urls',
    DATABASES={
        'default': {
            'ENGINE': test_config['DB_ENGINE'],
            'NAME': test_config['DB_NAME'],
        }
    },
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
            #'CACHE': not settings.DEBUG,
            'BUNDLE_DIR_NAME': 'bundles/',
            'STATS_FILE': os.path.join(VUE_FRONTEND_DIR, 'webpack-stats.json'),
            'POLL_INTERVAL': 0.1,
            'TIMEOUT': None,
            'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
        }
    },
)

django.setup()

execute_from_command_line(sys.argv)
