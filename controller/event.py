#!/usr/bin/env python2
#coding=utf-8

from datetime import datetime
import logging

import web
from google.appengine.api import users
from icalendar import Calendar, Event, UTC
from google.appengine.api import urlfetch
from BeautifulSoup import BeautifulStoneSoup

from environment import render
from model.dbevent import Dbevent
#from model.calendar import Calendar

routes = (
    '/test', 'Test',
    '/location/add', 'Add',
    '/location/(.+)', 'Get',
)

apikey = '0a4b03a80958ff351ee10af81c0afd9f'

class Get:
    def GET(self, location):
        web.header('Content-Type', 'text/plain;charset=UTF-8')

        cal = Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')
        cal.add('X-WR-CALDESC','豆瓣%s活动日历' %location)
        cal.add('CLASS', 'PUBLIC')
        cal.add('DESCRIPTION', 'dbevent2gc - 豆瓣%s活动日历' %location)

        dbevents = Dbevent.all()
        dbevents.filter('location_id =', location)
        events = [dbevent2event(e) for e in dbevents]
        for e in events:
            cal.add_component(e)

        return cal.as_string()

class Add:
    def GET(self):
        dbevent = Dbevent(
            id=1,
            title=u'活动1',
            category=u'派对',
            summary = u'派对',
            location_id = u'nanjing',
            location_name = u'南京',
            end_time = datetime.now(),
            url = 'http://api.douban.com/event/10082084',
            )

        dbevent.put()
        return 'add ok'

class Test:
    def GET(self):
        location = 'nanjing'
        web.header('Content-Type', 'text/plain;charset=UTF-8')

        cal = Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')
        cal.add('X-WR-CALDESC', u'豆瓣%s活动日历' %location)
        cal.add('CLASS', 'PUBLIC')
        cal.add('DESCRIPTION', u'dbevent2gc - 豆瓣%s活动日历' %location)

        xml = fetchEvent(location)
        
        events = xml2dbevents(xml)
        for e in events:
            cal.add_component(dbevent2event(e))

        return cal.as_string()

def dbevent2event(dbevent):
    """转换豆瓣数据模型到iCal数据模型"""
    event = Event()
    event.add('summary', dbevent.summary)
    event.add('content', dbevent.content)
    logging.info( dbevent.start_time)
    #event.add('dtstart', datetime(2005,4,4,8,0,0,tzinfo=UTC))
    event.add('dtend', dbevent.end_time)
    event.add('dtstamp', datetime(2005,4,4,0,10,0,tzinfo=UTC))
    event['uid'] = dbevent.id
    return event

def fetchEvent(location):
    """从豆瓣api获取数据"""
    url = 'http://api.douban.com/event/location/%s?apikey=%s' %(location, apikey)
    result = urlfetch.fetch(url)
    if result.status_code == 200:
        return result.content
    else:
        raise Exception('get events from douban.com failed')

def xml2dbevents(xml):
    """使用beautifulsoup转换html到Dbevent"""
    soup = BeautifulStoneSoup(xml)
    entrys = soup.findAll('entry')
    events = []
    for entry in entrys:
        events.append(entry2dbevent(entry))
    return events

def entry2dbevent(entry):
    """转换entry xml到dbevent"""
    url = entry.id.string
    id = int(url.split('/')[-1])

    title = entry.title.string
    category = entry.category['term'].split('#')[-1]
    summary = entry.summary.string #.replace(r'\n', '</br>')
    content = entry.content.string

    if entry.find('db:attribute',
                  attrs={'name':'invite_only'}).string == 'yes':
        invite_only = True
    else:
        invite_only = False
    if entry.find('db:attribute',
                  attrs={'name':'invite_only'}).string == 'yes':
        can_invite = True
    else:
        can_invite = False
    participants = int(entry.find('db:attribute',
                                  attrs={'name':'participants'}).string)
    wishers  = int(entry.find('db:attribute',
                                  attrs={'name':'wishers'}).string)
    album  = int(entry.find('db:attribute',
                                  attrs={'name':'album'}).string)
    location  = entry.find('db:location')
    location_id = location['id']
    location_name = location.string
    #start_time = entry.find('gd:when').attrMap['startTime']
    #end_time = entry.find('gd:when').attrMap['endtime']
    #where = entry.find('gd:where').attrMap['valuestring']

    geo_x = None #TODO 坐标
    geo_y = None

    dbevent = Dbevent(
        id=id,
        title=title,
        category=category,
        summary=summary,
        content=content,
        location_id=location_id,
        location_name=location_name,
        end_time = datetime.now(),
        url = url,
        )

    return dbevent


app = web.application(routes, locals())

