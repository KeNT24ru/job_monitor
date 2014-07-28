# -*- coding: utf-8 -*-
import logging
from collections import Counter
import json

from django.shortcuts import redirect, get_object_or_404, render
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse

from common.pagination import paginate

from database import db

VALID_STATUS_LIST = ('new', 'read')

def parse_keywords():
    res = set()
    for query, tag in settings.QUERY_LIST:
        for word in query.split():
            res.add(word.lower())
    return list(res)
       

def home_page(request):
    context = {}
    return render(request, 'job/home_page.html', context)


def api_project_list(request):
    active_status = request.GET.get('status', 'new')
    active_tag = request.GET.get('tag', 'web scraping') 
    active_service = request.GET.get('service', 'all')

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

    project_items = []
    for project in projects:
        project_items.append({
            'url': project['url'],
            'title': project['title'],
            'description': project['description'],
            'date': project['date'].strftime('%Y-%m-%dT%H:%M:%S'),
            'country': project['country'],
            'category': project['category'],
            'status': project['status'],
            'service': project['service'],
            'id': project['_id'],
        })
    content = json.dumps({
        'projects': project_items, 
        'highlight_keywords': parse_keywords(),
        'tags': sorted(tags.items(), key=lambda x: x[0]),
        'services': services,
        'statuses': sorted(statuses.items(), key=lambda x: x[0]),
    })
    return HttpResponse(content, content_type='application/json')


def api_project_bulk_update(request):
    status = request.POST['status']
    tag = request.POST['tag']
    service = request.POST['service']

    status_update = request.POST['update_status']

    query = {}
    if status:
        query['status'] = status
    if tag:
        query['tags'] = tag
    if service and service != 'all':
        query['service'] = service

    res = db.project.update(
        query,
        {'$set': {'status': status_update}},
        multi=True,
    )
    content = json.dumps({
        'status': 'ok',
        'messages': [
            {'type': 'info', 'content': 'Updated %d projects' % res['n']},
        ]
    })
    return HttpResponse(content, content_type='application/json')


def api_project_update(request):
    pid = request.POST['project_id']
    status_update = request.POST['update_status']

    project = db.project.find_one({'_id': pid})
    db.project.update(
        {'_id': project['_id']},
        {'$set': {'status': status_update}},
    )
    content = json.dumps({
        'status': 'ok',
        'messages': [
            #{'type': 'info', 'content': 'Project updated'},
        ]
    })
    return HttpResponse(content, content_type='application/json')
