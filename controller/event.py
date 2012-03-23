#!/usr/bin/env python2
#coding=utf-8

import logging

import web
from google.appengine.api import users
from google.appengine.ext import db

from environment import render
from model.dbevent import Dbevent
from model.calendar import Calendar
from controller.sync import Sync, SyncLocation

routes = (
    '/test', 'Test',
    '/sync-location', 'SyncLocation',
    '/sync', 'Sync',
    '/location/(.+)/update', 'Update',
    '/location/(.+)/delete', 'Delete',
    '/location/(.+)', 'Get',
)

class Get:
    def GET(self, location):
        web.header('Content-Type', 'text/plain;charset=UTF-8')
        params = web.input(type='all', length=None) # web.py post/get默认值
        category = params.type # 活动类型
        length = params.length # 活动长度
        if length is not None and length.isdigit() and length > 0:
            length = int(length)
        else:
            length = None

        calendar = Calendar.getCalendar(location, category, length)
        try:
            return calendar.getICalendarStr()
        except ValueError, e:
            raise web.notfound()

class Update:
    def GET(self, location):
        return Dbevent.updateDb(location)

class Delete:
    def GET(self, location):
        return Dbevent.deleteDb(location)

class Test:
    def GET(self):
        raise web.notfound()

        location = 'nanjing'
        category = 'all'
        #xml = fetchEvent(location, category=category, start=50, max=50)
        #dbevents_new = xml2dbevents(xml)

        #db.put(dbevents_new)

        return 'ok'

app = web.application(routes, locals())

# vim: set ft=python:
