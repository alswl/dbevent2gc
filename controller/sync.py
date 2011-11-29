#!/usr/bin/env python2
#coding=utf-8

from google.appengine.ext import db

from model.dbevent import xml2dbevents
from util.doubanapi import fetchEvent

class Sync:
    """同步数据库活动"""
    def GET(self):
        location_id = 'nanjing'
        self.__sync_location__(location_id)

        return 'ok'

    def __sync_location__(self, location):
        """同步某一个城市数据库活动"""
        xml = fetchEvent(location, category='all', start=0, max=50)
        dbevents= xml2dbevents(xml)

        db.put(dbevents)
