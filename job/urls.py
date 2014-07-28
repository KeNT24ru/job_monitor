# -*- coding: utf-8 -*-
from django.conf.urls import *

urlpatterns = patterns('job.views',
    url(r'^$', 'home_page', name='home_page'),
    url(r'^project/bulk/status/([^/]+)$', 'set_bulk_project_status', name='set_bulk_project_status'),
    url(r'^project/([-a-z0-9]+)/status/([^/]+)$', 'set_project_status', name='set_project_status'),
    # API
    url(r'^api/project$', 'api_project_list', name='api_project_list'),
    url(r'^api/project/bulk$', 'api_project_bulk_update', name='api_project_bulk_update'),
    url(r'^api/project/update$', 'api_project_update', name='api_project_update'),
)
