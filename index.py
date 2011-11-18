#!/usr/bin/env python2
#coding=utf-8

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
import web
from web.contrib.template import render_mako

routes = (
    '/(.*)', 'Index'
)

#web.config.debug = True

app = web.application(routes, globals())

render = render_mako(
    directories=['templates'],
    input_encoding='utf-8',
    output_encoding='utf-8',
    )

class Index:
    def GET(self, name):
        userinfo = users.get_current_user()
        return render.index()

def main():
    application = app.wsgifunc()
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

