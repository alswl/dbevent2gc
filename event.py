#!/usr/bin/env python2
#coding=utf-8

import web
from google.appengine.api import users

from environment import render

routes = (
    '/location/(.+)', 'Location',
)

class Location:
    def GET(self, location):
        web.header('Content-Type', 'text/plain;charset=UTF-8')
        return render.ical()

app = web.application(routes, locals())
