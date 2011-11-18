#!/usr/bin/env python2
#coding=utf-8

import web
from google.appengine.api import users

from environment import render

routes = (
    '', 'Index',
    'about', 'About',
)

class Index:
    def GET(self):
        userinfo = users.get_current_user()
        return render.index()

class About:
    def GET(self):
        return render.about()


app = web.application(routes, locals())
