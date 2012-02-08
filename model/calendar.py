#!/usr/bin/env python2
#coding=utf-8

from datetime import datetime
import logging

from google.appengine.ext import db
from icalendar import Calendar as ICalendar, Event, UTC

from model.dbevent import Dbevent, xml2dbevents
from model.syncqueue import SyncQueue
from util.doubanapi import fetchEvent

categoryMap = {
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


class Calendar(db.Model):
    """日历数据模型"""

    name = db.StringProperty(required=True)
    timezone = db.StringProperty(required=True)
    desc = db.StringProperty()
    category = db.StringProperty(required=True)
    length = db.IntegerProperty() # 日历查询的长度条件
    dtstamp = db.DateTimeProperty(required=True) # 时间标记

def getCalendar(location, category='all', length=None):
    """
    获取现成的日历，读取顺序为Memcache/Database
    """
    cal = ICalendar()
    cal.add('prodid', '-//Google Inc//Google Calendar 70.9054//EN')
    cal.add('version', '2.0')
    cal.add('X-WR-TIMEZONE', 'Asia/Shanghai')
    cal.add('CLASS', 'PUBLIC')
    cal.add('METHOD', 'PUBLISH')
    cal.add('CALSCALE', 'GREGORIAN')
    cal.add('X-WR-CALNAME', u'豆瓣%s - %s活动' \
            %(location, categoryMap[category]))
    desc = u'dbevent2gc - 豆瓣%s - %s活动 \n' \
            %(location, categoryMap[category])
    if length != None:
        desc += u'活动时间长度：%d小时以内' %length
    desc += u'via https://github.com/alswl/dbevent2gc\n' \
            u'by alswl(http://log4d.com)'
    cal.add('X-WR-CALDESC', desc)
    cal['dtstamp'] = datetime.strftime(datetime.now(), '%Y%m%dT%H%M%SZ')

    query = getDbevents(location, category, length)

    #result = query.fetch()
    result = sorted(query, key=lambda i: -i.id) #FIXME 使用内存排序
    #活动转换到iCalendar Event
    events = [e.parse_event() for e in result]
    for e in events:
        cal.add_component(e)

    return cal.as_string()

def getDbevents(location_id, category, length=None, start=0, count=50):
    """
    从数据库获取dbevents的query，如果取不到就去豆瓣同步
    """

    dbevents = getDbeventsQueryFromDb(location_id,
                                      category,
                                      length,
                                      start,
                                      count)

    if dbevents.count() == 0: #如果数据库没有值，则去实时查询
        xml = fetchEvent(location_id, category=category)
        dbevents_new = xml2dbevents(xml)
        db.put(dbevents_new)
        SyncQueue(key_name=location_id,
                  location=location_id,
                  last_sync=datetime(1988, 12, 24)).put()
        #db.run_in_transaction(lambda i, j: db.put(i) and db.put(j),
                             #dbevents_new, #FIXME 加入事务
                             #sysQueue)

    return getDbeventsQueryFromDb(location_id,
                                  category,
                                  length,
                                  start,
                                  count)

def getDbeventsQueryFromDb(location_id, category, length, start, count):
    """内函数"""
    dbevents = Dbevent.all() #从数据库获取数据
    dbevents.filter('location_id =', location_id) #地点
    if category != 'all': #类别
        dbevents.filter('category =', 'event.' + category)
    if isinstance(length, int) and length > 0: #活动长度
        dbevents.filter('length <=', length)
    #dbevents.order("-length") #TODO 使用排序
    return dbevents
