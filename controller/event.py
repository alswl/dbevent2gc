#!/usr/bin/env python2
#coding=utf-8

from datetime import datetime
import logging

import web
from google.appengine.api import users
from icalendar import Calendar, Event, UTC

from environment import render
from model.dbevent import Dbevent
#from model.calendar import Calendar

routes = (
    '/location/add', 'Add',
    '/location/(.+)', 'Get',
)

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

def dbevent2event(dbevent):
    """转换豆瓣数据模型到iCal数据模型"""
    event = Event()
    event.add('summary', dbevent.summary)
    logging.info( dbevent.start_time)
    #event.add('dtstart', datetime(2005,4,4,8,0,0,tzinfo=UTC))
    event.add('dtend', dbevent.end_time)
    event.add('dtstamp', datetime(2005,4,4,0,10,0,tzinfo=UTC))
    event['uid'] = dbevent.id
    return event

app = web.application(routes, locals())

