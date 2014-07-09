# -*- coding: utf-8 -*-
import logging

from django.shortcuts import redirect, get_object_or_404, render
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404

from common.pagination import paginate

from database import db
from spider import QUERY_LIST

VALID_STATUS_LIST = ('new', 'ok', 'offtopic')

def parse_keywords():
    res = set()
    for query in QUERY_LIST:
        for word in query.split():
            res.add(word.lower())
    return res
       

def home_page(request):
    status = request.GET.get('status', None)
    if not status in VALID_STATUS_LIST:
        status = 'new'
    projects = list(db.project.find({'status': status}, sort=[('date', -1)]))
    for proj in projects:
        proj['id'] = proj['_id']
    context = {'projects': projects,
               'keywords': ' '.join(parse_keywords()),
               'new_count': db.project.find({'status': 'new'}).count(),
               'ok_count': db.project.find({'status': 'ok'}).count(),
               'offtopic_count': db.project.find({'status': 'offtopic'}).count(),
               'status': status,
            }
    return render(request, 'job/home_page.html', context)


def set_project_status(request, pid, status):
    if not status in ('ok', 'offtopic'):
        raise Exception('Unknown status: %s' % status)
    project = db.project.find_one({'_id': pid})
    if project is None:
        raise Http404('Unknown project')
    db.project.update(
        {'_id': project['_id']},
        {'$set': {'status': status}},
    )
    return redirect('job:home_page')
