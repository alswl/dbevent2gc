#!/usr/bin/env python2
#coding=utf-8

import sys

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import web
from web.contrib.template import render_mako

import controller.index as index
import controller.event as event

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

#定义404
def notfound():
    return web.notfound(u'oh, shit, 404 notfound!')

#定义500
def internalerror():
    return web.internalerror(u'oh, shit, 500 error!')

app = web.application(routes, locals())
app.notfound = notfound

app.internalerror = internalerror


def main():
    application = app.wsgifunc()
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

