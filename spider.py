from django.conf import settings

from grab.spider import Spider, Task
from datetime import datetime
from grab import Grab
import urllib
from grab.tools.lxml_tools import render_html, parse_html, get_node_text, drop_node
from grab.tools.html import strip_tags, decode_entities
from copy import deepcopy
import re

from database import db


def compile_rex_list(input_list):
    return [re.compile(r'\b%s\b' % re.escape(x), re.U) for x in input_list]

REX_TITLE_KEY_BLACK_LIST = compile_rex_list(settings.TITLE_KEY_BLACK_LIST)
REX_COMMON_KEY_BLACK_LIST = compile_rex_list(settings.COMMON_KEY_BLACK_LIST)

def build_key_rex(query):
    rex_body = ''
    words = query.split()
    for count, word in enumerate(words):
        rex_body += re.escape(word.lower())
        if not count == len(words) - 1:
            rex_body += '\s+'
            rex_body += '(?:[-\w]+\s+)?'
    return re.compile(rex_body, re.U)


KEY_MATCH_LIST = [build_key_rex(x[0]) for x in settings.QUERY_LIST]


def check_keywords(keys, where):
    if any(x.search(where.lower()) for x in keys):
        return True
    return False


class JobSpider(object):
    def parse_date(self, text):
        dt = datetime.strptime(text.split(' +')[0].split(' EDT')[0].split(', ')[1], '%d %b %Y %H:%M:%S')
        return dt

    def task_generator(self):
        for query, tag in settings.QUERY_LIST:
            g = Grab()
            g.setup(url=self.build_query_url(query), content_type='xml')
            yield Task('feed', grab=g, query=query, tag=tag)

    def task_feed(self, grab, task):
        for project in self.parse_projects(grab):
            status1 = 'NO'
            status2 = 'NO'
            if any(x in project['category'] for x in settings.CAT_WHITE_LIST[self.service]):
                if (
                    check_keywords(KEY_MATCH_LIST, project['title']) or
                    check_keywords(KEY_MATCH_LIST, project['description'])
                ):
                    status1 = 'YES'
                    if not check_keywords(REX_TITLE_KEY_BLACK_LIST, project['title']):
                        if not check_keywords(REX_COMMON_KEY_BLACK_LIST, project['description']):
                            status2 = 'YES'
                            details = {
                                'service': self.service,
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
                                    {'$set': details, '$addToSet': {'tags': task.tag}},
                                )
                            else:
                                details['status'] = 'new'
                                details['tags'] = [task.tag]
                                db.project.save(details)
            print 'TITLE: %s' % project['title']
            print 'URL: %s' % project['url']
            print 'DESC: %s' % project['description'][:10000]
            print 'STATUS1: %s' % status1
            print 'STATUS2: %s' % status2
            print 'TAG: %s' % task.tag
            print '---------------------------------------------------------------'
            #import pdb; pdb.set_trace()


class OdeskSpider(JobSpider, Spider):
    service = 'odesk'

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
        res = []
        for elem in grab.doc('//item'):
            desc_node = parse_html(elem.select('description').text())
            res.append({
                'title': decode_entities(elem.select('title').text()),
                'description': self.parse_project_description(desc_node),
                'date': self.parse_date(elem.select('pubDate').text()),
                'category': self.parse_category(desc_node),
                'country': self.parse_country(desc_node),
                'id': 'odesk-%s' % self.parse_id(desc_node),
                'url': elem.select('link').text(),
            })
        return res

    def build_query_url(self, query):
        return 'https://www.odesk.com/jobs/rss?q=%s' % urllib.quote('"%s"' % query)



class ElanceSpider(JobSpider, Spider):
    service = 'elance'

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
                'title': decode_entities(elem.select('title').text()).replace(u' | Elance Job', u''),
                'description': self.parse_project_description(desc_node),
                'date': self.parse_date(elem.select('pubDate').text()),
                'category': self.parse_category(desc_node),
                'country': self.parse_country(desc_node),
                'id': 'elance-%s' % self.parse_id(desc_node),
                'url': elem.select('link').text(),
            })
        return res

    def build_query_url(self, query):
        return 'https://www.elance.com/r/rss/jobs/q-%s/cat-it-programming' % urllib.quote(query)

