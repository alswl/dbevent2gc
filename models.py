#!/usr/bin/env python2
#coding=utf-8

from google.appengine.ext import db

class TodoItem(db.Model):
    author = db.UserProperty()
    content = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
