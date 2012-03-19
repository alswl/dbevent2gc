#!/usr/bin/env python2
#coding=utf-8

from google.appengine.ext import db

class SyncQueue(db.Model):
    """同步队列"""

    location_id = db.StringProperty(required=True) #城市id/拼音
    update_at = db.DateTimeProperty()
