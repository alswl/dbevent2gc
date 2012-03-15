#!/usr/bin/env python2
#coding=utf-8

from datetime import datetime
import logging

from google.appengine.ext import db
from google.appengine.api import memcache
from icalendar import Calendar as ICalendar, Event, UTC

from config import config
from model.dbevent import Dbevent, xml2dbevents
from model.syncqueue import SyncQueue
from util.doubanapi import fetchEvent
from util.utc import get_utc_datetime

class Calendar(db.Model):
    """日历"""

    location = db.StringProperty(required=True) # 城市名称
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
    def getCalendar(location):
        """
        根据参数获取日历，读取顺序为Memcache/Database
        """
        query = db.Query(Calendar)
        query.filter('location =', location)
        calendar = query.get()
        if calendar is None:
            calendar = Calendar(location=location,
                               create_at=datetime.now())
            calendar.put()
        return calendar

    def getICalendarStr(self, category, length=None):
        """获取该日历对应的 iCalendar 文本"""
        if not self._categoryMap.has_key(category):
            raise ValueError

        # 从MemCache获取数据
        cache = memcache.get('%s-%s-%s'
                              %(self.location, category, str(length)))
        if not cache is None:
            return cache

        string = self.__getICalendar(category, length).as_string()
        memcache.set('%s-%s-%s' %(self.location, category, str(length)),
                     string,
                     time=config['cache']['memcache_timeout'])
        return string

    def __getICalendar(self, category, length=None):
        """获取该日历对应的 iCalendar"""
        cal = ICalendar()
        cal.add('prodid', '-//Google Inc//Google Calendar 70.9054//EN')
        cal.add('version', '2.0')
        cal.add('X-WR-TIMEZONE', 'Asia/Shanghai')
        cal.add('CLASS', 'PUBLIC')
        cal.add('METHOD', 'PUBLISH')
        cal.add('CALSCALE', 'GREGORIAN')
        cal.add('X-WR-CALNAME', u'豆瓣%s - %s活动' \
                %(self.location, self._categoryMap[category]))
        desc = u'dbevent2gc - 豆瓣%s - %s活动 \n' \
                %(self.location, self._categoryMap[category])
        if not length is None:
            desc += u'活动时间长度：%d小时以内' %length
        desc += u'via https://github.com/alswl/dbevent2gc\n' \
                u'by alswl(http://log4d.com)'
        cal.add('X-WR-CALDESC', desc)
        cal['dtstamp'] = datetime.strftime(datetime.utcnow(),
                                           '%Y%m%dT%H%M%SZ')

        dbevents = getDbevents(self.location, category, length)

        #将活动添加到日历
        map(lambda e: cal.add_component(e.parse_event()), dbevents)
        return cal

    def updateDb(self):
        """更新日历中活动"""
        pass

    def deleteDb(self):
        """删除过期的活动"""
        pass

def getDbevents(location_id, category, length=None):
    """
    根据条件获取Dbevents
    """
    dbevents = []
    start = 1
    max = config['display']['page_count']

    # 当出现类型筛选时候，获取最近一周的，最多获取200个
    while (len(dbevents) == 0 or not isMoreThenAWeek(dbevents[-1])) \
          and len(dbevents) < max:
        xml = fetchEvent(location_id,
                         category=category,
                         max=50,
                         start=start)
        dbevents_new = xml2dbevents(xml)
        if not length is None:
            dbevents_new = [x for x in dbevents_new if x.length < length]
        if len(dbevents_new) == 0: # 豆瓣没了
            break
        dbevents += dbevents_new
        start += 50
    return dbevents

def isMoreThenAWeek(dbevent):
    """活动距今时间是否大于一周了"""
    delta = datetime.utcnow() - get_utc_datetime(dbevent.end_time)
    return delta.days > 7

def getDbeventsV1(location_id, category, length=None, start=0, count=50):
    """
    从数据库获取dbevents的query，如果取不到就去豆瓣同步
    """
    raise Exception

    dbevents = getDbeventsQueryFromDb(location_id,
                                      category,
                                      length,
                                      start,
                                      count)

    if dbevents.count() == 0: #如果数据库没有值，则去实时查询
        xml = fetchEvent(location_id, category=category)
        dbevents = xml2dbevents(xml)
        db.put(dbevents)
        SyncQueue(key_name=location_id,
                  location=location_id,
                  last_sync=datetime(1988, 12, 24)).put()
        #db.run_in_transaction(lambda i, j: db.put(i) and db.put(j),
                             #dbevents, #FIXME 加入事务
                             #sysQueue)

    return dbevents

def getDbeventsQueryFromDb(location_id, category, length, start, count):
    """从数据库查询dbevents"""
    dbevents = Dbevent.all() #从数据库获取数据
    dbevents.filter('location_id =', location_id) #地点
    if category != 'all': #类别
        dbevents.filter('category =', 'event.' + category)
    if isinstance(length, int) and length > 0: #活动长度
        dbevents.filter('length <=', length)
    #dbevents.order("-length") #TODO 使用排序
    return dbevents
