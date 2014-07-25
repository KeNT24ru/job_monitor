# -*- coding: utf-8 -*-
import logging
from collections import Counter

from django.shortcuts import redirect, get_object_or_404, render
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404

from common.pagination import paginate

from database import db

VALID_STATUS_LIST = ('new', 'read')

def parse_keywords():
    res = set()
    for query, tag in settings.QUERY_LIST:
        for word in query.split():
            res.add(word.lower())
    return res
       

def home_page(request):
    active_status = request.GET.get('status', None)
    active_tag = request.GET.get('tag', 'web scraping') 
    active_service = request.GET.get('service', 'all')

    if not active_status in VALID_STATUS_LIST:
        active_status = 'new'

    query = {'status': active_status}
    if active_tag:
        query['tags'] = active_tag
    if active_service and active_service != 'all':
        query['service'] = active_service
    projects = list(db.project.find(query, sort=[('date', -1)]))
    for proj in projects:
        proj['id'] = proj['_id']

    tags = {}
    for project in db.project.find({}, {'tags': 1}):
        for tag in project.get('tags', []):
            if not tag in tags:
                tags[tag] = 0

    for tag in tags:
        query = {'status': active_status, 'tags': tag}
        if active_service and active_service != 'all':
            query['service'] = active_service
        tags[tag] = db.project.find(query).count()


    statuses = {}.fromkeys(VALID_STATUS_LIST, 0)
    for status in statuses:
        query = {'status': status}
        if active_service and active_service != 'all':
            query['service'] = active_service
        if active_tag:
            query['tags'] = active_tag
        statuses[status] = db.project.find(query).count()

    service_names = ('all', 'odesk', 'elance')
    services = []
    for sname in service_names:
        query = {'status': status}
        if sname != 'all':
            query['service'] = sname
        if active_tag:
            query['tags'] = active_tag
        services.append((sname, db.project.find(query).count()))

    context = {'projects': projects,
               'project_ids_csv': ','.join(x['_id'] for x in projects),
               'keywords': ' '.join(parse_keywords()),
               'active_status': active_status,
               'active_tag': active_tag,
               'active_service': active_service,
               'tags': sorted(tags.items(), key=lambda x: x[0]),
               'services': services,
               'statuses': sorted(statuses.items(), key=lambda x: x[0]),
            }
    return render(request, 'job/home_page.html', context)


def set_project_status(request, pid, status):
    if not status in VALID_STATUS_LIST:
        raise Exception('Unknown status: %s' % status)
    project = db.project.find_one({'_id': pid})
    if project is None:
        raise Http404('Unknown project')
    db.project.update(
        {'_id': project['_id']},
        {'$set': {'status': status}},
    )
    return redirect(request.META.get('HTTP_REFERER', reverse('job:home_page')))


def set_bulk_project_status(request, status):
    status = request.GET.get('status')
    tag = request.GET.get('tag')
    service = request.GET.get('service', 'all')

    query = {}
    if status:
        query['status'] = status
    if tag:
        query['tags'] = tag
    if service and service != 'all':
        query['service'] = service

    db.project.update(
        query,
        {'$set': {'status': 'read'}},
        multi=True,
    )
    return redirect(request.META.get('HTTP_REFERER', reverse('job:home_page')))
