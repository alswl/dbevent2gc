#!/usr/bin/env python2
#coding=utf-8

from google.appengine.ext import db

class Calendar(db.Model):
    """日历数据模型"""

    name = db.StringProperty(required=True)
    timezone = db.StringProperty(required=True)
    description = db.StringProperty()
