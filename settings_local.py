# -*- coding: utf-8 -*-
SECRET_KEY = 'j)o17o#gn-5w5$j8(qd=14kub^_6js6lwen0rhi%x2wbj3^@pk'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
HOSTNAME = 'localhost:8000'
INTERNAL_IPS = ('127.0.0.1',)
DEBUG = TEMPLATE_DEBUG = True

# Debug Toolbar
#from settings import MIDDLEWARE_CLASSES, INSTALLED_APPS
#MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
#INSTALLED_APPS += ('debug_toolbar',)
