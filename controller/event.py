#!/usr/bin/env python2
#coding=utf-8

import datetime
import logging

import web
from google.appengine.api import users

from environment import render
from model.event import Event
from model.calendar import Calendar

routes = (
    '/location/add', 'Add',
    '/location/(.+)', 'Get',
)

class Get:
    def GET(self, location):
        web.header('Content-Type', 'text/plain;charset=UTF-8')

        calendar = Calendar(name=u'豆瓣同城活动日历',
                            timezone='Asia/Shanghai',
                            description=u'dbevent2gc - 豆瓣同城活动日历'
                           )

        events = Event.all()
        events.filter('location =', location)

        return render.ical(calendar=calendar, events=events)

class Add:
    def GET(self):
        #TODO 写入失败
        event = Event(
            id='1',
            title=u'活动1',
            category=u'派对',
            summary = u'派对',
            location = u'南京',
            end_time = datetime.datetime.now()
            )

        #logging.debug(event.category)

        event.put()
        return 'add ok'

app = web.application(routes, locals())

