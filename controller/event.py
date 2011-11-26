#!/usr/bin/env python2
#coding=utf-8

from datetime import datetime
import logging

import web
from google.appengine.api import users
from icalendar import Calendar, Event, UTC
from google.appengine.api import urlfetch
from BeautifulSoup import BeautifulStoneSoup
import iso8601

from environment import render
from model.dbevent import Dbevent
#from model.calendar import Calendar

routes = (
    '/test', 'Test',
    '/location/add', 'Add',
    '/location/(.+)', 'Get',
)

apikey = '0a4b03a80958ff351ee10af81c0afd9f'
event_type_map = {
    'all': '所有类型',
    'music': '音乐/演出',
    'exhibition': '展览',
    'film': '电影',
    'salon': '讲座/沙龙',
    'drama': '戏剧/曲艺',
    'party': '生活/聚会',
    'sports': '体育',
    'travel': '旅行',
    'commonweal': '公益',
    'others': '其他',
}

class Get:
    def GET(self, location):
        web.header('Content-Type', 'text/plain;charset=UTF-8')
        params = web.input(type='all') #web.py post/get默认值
        event_type = params.type
        if event_type not in event_type_map: #处理意外的type参数
            event_type = 'all'
        event_type = event_type.strip()

        cal = Calendar()
        cal.add('prodid', '-//Google Inc//Google Calendar 70.9054//EN')
        cal.add('version', '2.0')
        cal.add('X-WR-TIMEZONE', 'Asia/Shanghai')
        cal.add('CLASS', 'PUBLIC')
        cal.add('METHOD', 'PUBLISH')
        cal.add('CALSCALE', 'GREGORIAN')
        cal.add('X-WR-CALNAME', '豆瓣%s - %s活动' \
                %(location, event_type_map[event_type]))
        cal.add('X-WR-CALDESC',
                'dbevent2gc - 豆瓣%s - %s活动 \n' \
                'via http://dbevent2gc.appspot.com\n' \
                'by alswl(http://log4d.com)' \
                %(location, event_type_map[event_type]))
        #cal.add('DTSTAMP', datetime.now())
        cal['dtstamp'] = datetime.strftime(datetime.now(), '%Y%m%dT%H%M%SZ')

        #dbevents = Dbevent.all()
        #dbevents.filter('location_id =', location)
        #events = [dbevent2event(e) for e in dbevents]

        xml = fetchEvent(location, event_type=event_type) #TODO try...catch

        events = xml2dbevents(xml)
        for e in events:
            cal.add_component(dbevent2event(e))

        return cal.as_string()

class Add:
    def GET(self):
        dbevent = Dbevent(
            id=id,
            title=title,
            self_link=self_link,
            alternate_link=alternate_link,
            category=category,
            summary=summary,
            content=content,
            location_id=location_id,
            location_name=location_name,
            start_time=start_time,
            end_time=end_time,
            where=where,
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
    event.add('summary', dbevent.title)
    desc = dbevent.summary
    if isinstance(dbevent.participants, int):
        desc += '\n\n' + u'参与人数 %d, 感兴趣人数 %d' \
                %(dbevent.participants, dbevent.wishers)
    desc += '\n\n' + dbevent.alternate_link
    event.add('DESCRIPTION', desc)
    #event.add('dtstart', dbevent.start_time)
    event['dtstart'] = datetime.strftime(dbevent.start_time, '%Y%m%dT%H%M%SZ')
    #event.add('dtend', dbevent.end_time)
    event['dtend'] = datetime.strftime(dbevent.end_time, '%Y%m%dT%H%M%SZ')
    event.add('STATUS', 'CONFIRMED')
    location = dbevent.where
    if dbevent.geo_point != None:
        location += u' @(%s)' %dbevent.geo_point
    event.add('location', location)
    #event.add('dtstamp', datetime.now())
    event['dtstamp'] = datetime.strftime(datetime.now(), '%Y%m%dT%H%M%SZ')
    event['uid'] = dbevent.id
    return event

def fetchEvent(location, event_type='all', max=50):
    """从豆瓣api获取数据"""
    url = 'http://api.douban.com/event/location/%s?' \
            'type=%s&max-results=%d&apikey=%s' %(location,
                                                event_type,
                                                max,
                                                apikey)
    logging.info('fetch events from douban url: %s'%url)
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
    self_link = entry.find('link', attrs={'rel': 'self'})['href']
    id = int(self_link.split('/')[-1])

    title = entry.title.string
    category = entry.category['term'].split('#')[-1]
    alternate_link = entry.find('link', attrs={'rel': 'alternate'})['href']
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
    start_time = iso8601.parse_date(entry.find('gd:when')['starttime'])
    end_time = iso8601.parse_date(entry.find('gd:when')['endtime'])
    where = entry.find('gd:where')['valuestring']

    dbevent = Dbevent(
        id=id,
        title=title,
        self_link=self_link,
        alternate_link=alternate_link,
        category=category,
        summary=summary,
        content=content,
        participants=participants,
        wishers=wishers,
        location_id=location_id,
        location_name=location_name,
        start_time=start_time,
        end_time=end_time,
        where=where,
        )

    geo_point = entry.find('georss:point')
    if geo_point != None:
        dbevent.geo_point = geo_point.string


    return dbevent


app = web.application(routes, locals())

