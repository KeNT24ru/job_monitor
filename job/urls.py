# -*- coding: utf-8 -*-
from django.conf.urls import *

urlpatterns = patterns('job.views',
    url(r'^$', 'home_page', name='home_page'),
    url(r'^project/bulk/status/([^/]+)$', 'set_bulk_project_status', name='set_bulk_project_status'),
    url(r'^project/([-a-z0-9]+)/status/([^/]+)$', 'set_project_status', name='set_project_status'),
)
