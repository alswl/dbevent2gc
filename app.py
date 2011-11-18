#!/usr/bin/env python2
#coding=utf-8

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import web
from web.contrib.template import render_mako

import index

routes = (
    '/', index.app
)

web.config.debug = True

app = web.application(routes, locals())

def main():
    application = app.wsgifunc()
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

