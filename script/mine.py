from database import db
from spider import check_keywords

def main(**kwargs):
    for proj in db.project.find({'status': 'ok'}):
        if not check_keywords(proj):
            print u'TITLE: %s' % proj['title']
            print u'DESC: %s' % proj['description']
            print '-------------------------------------'
