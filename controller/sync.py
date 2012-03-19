#!/usr/bin/env python2
#coding=utf-8

from datetime import datetime
import logging

import web
from google.appengine.ext import db
from google.appengine.api.labs import taskqueue

from model.syncqueue import SyncQueue
from model.dbevent import Dbevent

class Sync:
    """同步数据库活动"""
    def GET(self):
        query = SyncQueue.all()
        result = query.fetch(1000)

        for syncQuery in result:
            taskqueue.add(queue_name='sync-location',
                          method='GET',
                          url='/event/sync-location',
                          params={
                              'location': syncQuery.location_id,
                          }
                         )

        return 'start sync'

class SyncLocation:
    """同步某个城市"""
    def GET(self):
        params = web.input()
        if not params.has_key('location'):
            raise web.seeother('../')
        location_id = params.location

        length_update = Dbevent.updateDb(location_id)
        length_delete = Dbevent.deleteDb(location_id)
        db.put(SyncQueue(key_name=location_id,
                         location_id=location_id,
                         update_at=datetime.utcnow()))
        logging.info('update %s %d' %(location_id, length_update))
        logging.info('delete %s %d' %(location_id, length_delete))

        return 'ok'
