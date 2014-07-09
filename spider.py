from grab.spider import Spider, Task
from datetime import datetime
from grab import Grab
import urllib
from grab.tools.lxml_tools import render_html, parse_html, get_node_text, drop_node
from grab.tools.html import strip_tags, decode_entities
from copy import deepcopy
import re

from database import db

ODESK_CAT_WHITE_LIST = (
    'Web Development',
    'Software Development',
)

ELANCE_CAT_WHITE_LIST = (
    'IT & Programming',
)

QUERY_LIST = (
    'data mining',
    'machine learning',
    'data analysis',
    'data science',
    #'statistics',
    'data extraction',
    'site scraping',
    'screen scraping',
    'site scraped',
    'data import',
    'import data',
    'process data',
    'load data',
    'analyzing data',
)

def build_key_rex(query):
    rex_body = ''
    words = query.split()
    for count, word in enumerate(words):
        rex_body += re.escape(word.lower())
        if not count == len(words) - 1:
            rex_body += '\s+'
            rex_body += '(?:[-\w]+\s+)?'
    return re.compile(rex_body, re.U)


KEYWORD_REX_LIST = [build_key_rex(x) for x in QUERY_LIST]


def check_keywords(proj):
    if any(x.search(proj['title'].lower()) for x in KEYWORD_REX_LIST):
        return True
    if any(x.search(proj['description'].lower()) for x in KEYWORD_REX_LIST):
        return True
    return False


class JobSpider(object):
    def parse_date(self, text):
        dt = datetime.strptime(text.split(' +')[0].split(' EDT')[0].split(', ')[1], '%d %b %Y %H:%M:%S')
        return dt


class OdeskSpider(Spider, JobSpider):
    def parse_project_description(self, root):
        for node in root.xpath('//br'):
            node.tail = (node.tail or '') + '\n'
        text = strip_tags(decode_entities(render_html(root, encoding='unicode')),
                          normalize_space=False)
        text = text.split(u'Posted On')[0].strip()
        text = text.split(u'Budget :')[0].strip()
        return text

    def parse_category(self, root):
        return unicode(root.xpath('.//b[text()="Category"]'
                                  '/following-sibling::text()')[0]).strip(' :')

    def parse_country(self, root):
        val = unicode(root.xpath('.//b[text()="Country"]'
                                  '/following-sibling::text()')[0]).strip(' :')
        return val

    def parse_id(self, root):
        return unicode(root.xpath('.//b[text()="ID"]'
                                  '/following-sibling::text()')[0]).strip(' :')

    def parse_projects(self, grab):
        for elem in grab.doc('//item'):
            desc_node = parse_html(elem.select('description').text())
            yield {
                'title': decode_entities(elem.select('title').text()),
                'description': self.parse_project_description(desc_node),
                'date': self.parse_date(elem.select('pubDate').text()),
                'category': self.parse_category(desc_node),
                'country': self.parse_country(desc_node),
                'id': 'odesk-%s' % self.parse_id(desc_node),
                'url': elem.select('link').text(),
            }

    def task_generator(self):
        for query in QUERY_LIST:
            g = Grab()
            g.setup(url=self.build_query_url('"%s"' % query), content_type='xml')
            yield Task('feed', grab=g)

    def build_query_url(self, query):
        return 'https://www.odesk.com/jobs/rss?q=%s' % urllib.quote(query)

    def task_feed(self, grab, task):
        for project in self.parse_projects(grab):
            print 'PROJECT:', project['title']
            if any(x in project['category'] for x in ODESK_CAT_WHITE_LIST):
                if check_keywords(project):
                    details = {
                        'service': 'odesk',
                        '_id': project['id'],
                        'title': project['title'],
                        'description': project['description'],
                        'date': project['date'],
                        'country': project['country'],
                        'category': project['category'],
                        'url': project['url'],
                    }
                    if db.project.find_one({'_id': details['_id']}):
                        pid = details['_id']
                        del details['_id']
                        db.project.update(
                            {'_id': pid},
                            {'$set': details},
                        )
                    else:
                        details['status'] = 'new'
                        db.project.save(details)


class ElanceSpider(Spider, JobSpider):
    def parse_project_description(self, root):
        for node in root.xpath('//br'):
            node.tail = (node.tail or '') + '\n'
        text = strip_tags(decode_entities(render_html(root, encoding='unicode')),
                          normalize_space=False)
        text = text.split(u'Category:')[0].strip()
        return text

    def parse_category(self, root):
        try:
            return unicode(root.xpath('.//b[text()="Category:"]'
                                      '/following-sibling::text()')[0]).strip(' :')
        except IndexError:
            return 'NA'

    def parse_country(self, root):
        val = unicode(root.xpath('.//b[text()="Client Location:"]'
                                  '/following-sibling::text()')[0]).strip(' :,')
        return val

    def parse_id(self, root):
        return unicode(root.xpath('.//b[text()="Job ID:"]'
                                  '/following-sibling::text()')[0]).strip(' :')

    def parse_projects(self, grab):
        res = []
        for elem in grab.doc('//item'):
            desc_node = parse_html(elem.select('description').text())
            res.append({
                'title': decode_entities(elem.select('title').text()).replace(' | Elance Job', ''),
                'description': self.parse_project_description(desc_node),
                'date': self.parse_date(elem.select('pubDate').text()),
                'category': self.parse_category(desc_node),
                'country': self.parse_country(desc_node),
                'id': 'elance-%s' % self.parse_id(desc_node),
                'url': elem.select('link').text(),
            })
        return res

    def task_generator(self):
        for query in QUERY_LIST:
            g = Grab()
            g.setup(url=self.build_query_url('%s' % query), content_type='xml')
            yield Task('feed', grab=g)

    def build_query_url(self, query):
        return 'https://www.elance.com/r/rss/jobs/q-%s/cat-it-programming' % urllib.quote(query)

    def task_feed(self, grab, task):
        for project in self.parse_projects(grab):
            print 'PROJECT:', project['title']
            if any(x in project['category'] for x in ELANCE_CAT_WHITE_LIST):
                if check_keywords(project):
                    details = {
                        'service': 'elance',
                        '_id': project['id'],
                        'title': project['title'],
                        'description': project['description'],
                        'date': project['date'],
                        'country': project['country'],
                        'category': project['category'],
                        'url': project['url'],
                    }
                    #for key, val in details.items():
                        #print key.upper()
                        #print u'  %s' % val
                    #print '-----------------------------'
                    if db.project.find_one({'_id': details['_id']}):
                        pid = details['_id']
                        del details['_id']
                        db.project.update(
                            {'_id': pid},
                            {'$set': details},
                        )
                    else:
                        details['status'] = 'new'
                        db.project.save(details)
