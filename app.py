#!/usr/bin/env python2
#coding=utf-8

import sys

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import web
from web.contrib.template import render_mako

import index
import event

#编码设置
code = sys.getdefaultencoding()
if code != 'utf8':
    reload(sys)
    sys.setdefaultencoding('utf8')

#主路由
routes = (
    '/event', event.app,
    '/', index.app,
)

#调试
web.config.debug = True

app = web.application(routes, locals())

def main():
    application = app.wsgifunc()
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

