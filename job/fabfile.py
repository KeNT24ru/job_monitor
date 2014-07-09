from __future__ import with_statement
from fabric import api
from fabric.contrib import django
import os

# Configuration
ENV_DIR = '.env'
REMOTE_ROOT = ''
api.env.user = 'web'
api.env.hosts = []

# Activate the virtualenv
try:
    activate_this = ENV_DIR + '/bin/activate_this.py'
    execfile(activate_this, dict(__file__=activate_this))
except IOError:
    pass
else:
    django.settings_module('settings')


def run():
    "Run debug server"

    api.local('./manage.py runserver 0.0.0.0:8000')


def run_plus():
    "Run debug server with werkzeug debugger"

    api.local('./manage.py runserver_plus 0.0.0.0:8000')


def buildenv():
    # Ignore "IOError: [Errno 26] Text file busy: 'var/.env/bin/python'"
    # when debug server is live
    with api.settings(warn_only=True):
        api.local('virtualenv --no-site-packages %s' % ENV_DIR, capture=False)
    api.local('%s/bin/easy_install pip' % ENV_DIR, capture=False)
    api.local('%s/bin/pip install --use-mirrors -r requirements.txt' % ENV_DIR, capture=False)


def shell():
    "Run shell_plus management command."

    api.local('./manage.py shell_plus')


def deploy():
    import settings

    api.local('hg push')
    with api.cd(REMOTE_ROOT):
        api.run('hg up')
        api.run('./manage.py syncdb --noinput')
        if 'south' in settings.INSTALLED_APPS:
            api.run('./manage.py migrate')
        api.run('touch app.py')


def update_lib(name):
    """
    Update dependency which has record in requirements.txt matched to given ``name``.
    """
    
    for line in open('requirements.txt'):
        if name in line:
            line = line.strip()
            if not line.startswith('#'):
                api.local('%s/bin/pip install --use-mirrors -U %s' % (ENV_DIR, line.strip()))


def automig(name):
    """
    Create auto south migration and apply it to database.
    """

    api.local('./manage.py schemamigration %s --auto' % name)
    api.local('./manage.py migrate %s' % name)
