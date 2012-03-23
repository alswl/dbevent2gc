#!/usr/bin/env python2
#coding=utf-8

from datetime import datetime
import logging

from google.appengine.ext import db
from google.appengine.api import memcache
from icalendar import Calendar as ICalendar, Event, UTC

from config import config
from model.dbevent import Dbevent
from model.syncqueue import SyncQueue
from util.doubanapi import fetchEvent
from util.utc import get_utc_datetime

class Calendar(db.Model):
    """日历"""

    location_id = db.StringProperty(required=True) # 城市名称
    #timezone = db.StringProperty(required=True) # 时区
    #desc = db.StringProperty()
    #category = db.StringProperty(required=True)
    #length = db.IntegerProperty() # 日历查询的长度条件
    #dtstamp = db.DateTimeProperty(required=True) # 时间标记
    update_at = db.DateTimeProperty()
    create_at = db.DateTimeProperty(required=True)

    _categoryMap = {
        'all': u'所有类型',
        'music': u'音乐/演出',
        'exhibition': u'展览',
        'film': u'电影',
        'salon': u'讲座/沙龙',
        'drama': u'戏剧/曲艺',
        'party': u'生活/聚会',
        'sports': u'体育',
        'travel': u'旅行',
        'commonweal': u'公益',
        'others': u'其他',
    }

    @staticmethod
    def getCalendar(location_id, category='all', length=None):
        """
        获取日历工厂方法
        """
        query = db.Query(Calendar)
        query.filter('location_id =', location_id)
        calendar = query.get()
        if calendar is None:
            calendar = Calendar(location_id=location_id,
                               create_at=datetime.now())
            calendar.put()
        calendar._category = category
        calendar._length = length
        return calendar

    def getICalendarStr(self):
        """获取该日历对应的 iCalendar 文本"""
        if not self._categoryMap.has_key(self._category):
            raise ValueError

        # 从MemCache获取数据
        cache = memcache.get('%s-%s-%s' %(self.location_id,
                                          self._category,
                                          str(self._length)))
        if not cache is None:
            return cache

        string = self.__getICalendar().as_string()
        memcache.set('%s-%s-%s' %(self.location_id, self._category,
                                  str(self._length)),
                     string,
                     time=config['cache']['memcache_timeout'])
        return string

    def __getICalendar(self):
        """获取该日历对应的 iCalendar"""
        cal = ICalendar()
        cal.add('prodid', '-//Google Inc//Google Calendar 70.9054//EN')
        cal.add('version', '2.0')
        cal.add('X-WR-TIMEZONE', 'Asia/Shanghai')
        cal.add('CLASS', 'PUBLIC')
        cal.add('METHOD', 'PUBLISH')
        cal.add('CALSCALE', 'GREGORIAN')
        cal.add('X-WR-CALNAME', u'豆瓣%s - %s活动' \
                %(self.location_id, self._categoryMap[self._category]))
        desc = u'dbevent2gc - 豆瓣%s - %s活动 \n' \
                %(self.location_id, self._categoryMap[self._category])
        if not self._length is None:
            desc += u'活动时间长度：%d小时以内' %self._length
        desc += u'via https://github.com/alswl/dbevent2gc\n' \
                u'by alswl(http://log4d.com)'
        cal.add('X-WR-CALDESC', desc)
        cal['dtstamp'] = datetime.strftime(datetime.utcnow(),
                                           '%Y%m%dT%H%M%SZ')

        dbevents = Dbevent.getDbevents(self.location_id, self._category,
                                       self._length)

        #将活动添加到日历
        map(lambda e: cal.add_component(e.parse_event()), dbevents)
        return cal

    def deleteMemcache(self):
        """清楚 MemCache 缓存"""
        memcache.delete('%s-%s-%s' %(self.location_id, self._category,
                                  str(self._length)))

    @staticmethod
    def deleteMemcacheCity(location_id):
        keys = []
        for k in Calendar._categoryMap:
            for l in [None, 3, 6, 12, 24, 48, 72, 168, 720]:
                keys.append('%s-%s-%s' %(location_id, k, str(l)))
        memcache.delete_multi(keys)
