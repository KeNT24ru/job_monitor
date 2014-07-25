# -*- coding: utf-8 -*-
# **************
# Initial config
# **************

import os.path
import sys

ROOT = os.path.dirname(os.path.realpath(__file__))

# ******
# Admins
# ******
ADMINS = (
    ('Grigoriy Petukhov', 'lorien@lorien.name'),
)
MANAGERS = ADMINS


# ****
# Time
# ****

TIME_ZONE = 'America/Chicago'
USE_TZ = False
DATETIME_FORMAT = 'd F, Y H:i'
DATE_FORMAT = 'd F, Y'


# ****
# I18N
# ****

LANGUAGE_CODE = 'ru-ru'
USE_I18N = True
USE_L10N = True


# ************
# Static Files
# ************

MEDIA_ROOT = os.path.join(ROOT, 'static')
MEDIA_URL = '/static/'
STATIC_ROOT = os.path.join(ROOT, 'static/pub')
STATIC_URL = '/static/pub/'
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


# *********
# Templates
# *********

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
TEMPLATE_DIRS = (
    os.path.join(ROOT, 'templates'),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    #'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
)


# ******************
# Apps & Middlewares
# ******************

MIDDLEWARE_CLASSES = (
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    #'django.middleware.transaction.TransactionMiddleware',
)

INSTALLED_APPS = (
    # django
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'django.contrib.admin',
    # 3rd party libraries
    'common',
    'django_extensions',
    #'south',
    'widget_tweaks',
    #'pytils',
    # local project modules
)


# *******
# Logging
# *******

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(name)s %(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'south': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}


# *****
# Debug
# *****

ALLOWED_HOSTS = []
DEBUG = False
TEMPLATE_DEBUG = DEBUG
TEST_DATABASE_CHARSET = 'utf8'
DEBUG_TOOLBAR_CONFIG  = {
    'INTERCEPT_REDIRECTS': False,
}

# *****
# Cache
# *****

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': '127.0.0.1:11211',
#    }
#}
#CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True


# **********************
# Miscellanious Settings
# **********************
#DEFAULT_FROM_EMAIL = 'robotdesconto.ru <noreply@desconto.ru>'
ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'app.application'
SITE_ID = 1

GRAB_SPIDER_MODULES = ['spider']
#GRAB_PROXY_LIST = {
    #'source': '/web/proxy.txt',
    #'source_type': 'text_file',
#}


from search_config import *

# **************
# Local settings
# **************
try:
    from settings_local import *
except ImportError:
    pass


# **********
# Secret Key
# **********

if not SECRET_KEY:
    raise Exception('You must provide SECRET_KEY value in settings_local.py')
