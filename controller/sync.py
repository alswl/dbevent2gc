#!/usr/bin/env python2
#coding=utf-8

from datetime import datetime
import logging

import web
from google.appengine.ext import db
from google.appengine.api.labs import taskqueue

from model.dbevent import xml2dbevents
from model.syncqueue import SyncQueue
from util.doubanapi import fetchEvent, getXmlCursor

class Sync:
    """同步数据库活动"""
    def GET(self):
        query = SyncQueue.all()
        query.order('last_sync')
        result = query.fetch(10)

        for syncQuery in result:
            taskqueue.add(queue_name='sync-location',
                          method='GET',
                          url='/event/sync-location',
                          params={'location': syncQuery.location,
                                  'start': '1'})

        return 'start sync'

class SyncLocation:
    """同步某个城市"""
    def GET(self):
        params = web.input()
        if not params.has_key('location') or not params.has_key('start'):
            raise web.seeother('../')
        location_id = params.location
        start = int(params.start)

        xml = fetchEvent(location_id, category='all', start=start, max=50)
        start, count, totalCount = getXmlCursor(xml)
        dbevents= xml2dbevents(xml)
        db.put(dbevents)

        if totalCount > start + count: #还有剩余，则加入队列
            taskqueue.add(queue_name='sync-location', url='/event/sync-location',
                          method='GET',
                          params={
                              'location': location_id,
                              'start': str(start + count),
                          })
        else: #写入最后同步实践
            db.put(SyncQueue(key_name=location_id,
                      location=location_id,
                      last_sync=datetime.now()))

        return 'ok'
