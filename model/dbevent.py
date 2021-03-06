#!/usr/bin/env python2
#coding=utf-8

import logging
from datetime import datetime, timedelta

from BeautifulSoup import BeautifulStoneSoup
from icalendar import Calendar, Event, UTC
import iso8601
from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import OverQuotaError

from config import config
from model.syncqueue import SyncQueue
from util.utc import get_utc_datetime
from util.doubanapi import fetchEvent
from util.error import GetDoubanDataError

class Dbevent(db.Model):
    """豆瓣同城事件数据模型"""

    id = db.IntegerProperty(required=True)
    title = db.StringProperty(required=True)
    self_link = db.StringProperty(required=True)
    image_link = db.LinkProperty() #TODO 活动照片
    alternate_link = db.StringProperty(required=True) #TODO 关联对象
    category = db.StringProperty(required=True)
    summary = db.TextProperty(required=True)
    content = db.TextProperty() #TODO 是否必填
    invite_only = db.BooleanProperty() #需要邀请才能参加
    can_invite = db.BooleanProperty() #允许参加者邀请其友邻来参加
    participants = db.IntegerProperty() #参与人数
    wishers = db.IntegerProperty() #想参加的人
    album = db.StringProperty() #TODO 这个属性干嘛的？
    status = db.StringProperty() #TODO 
    location_id = db.StringProperty(required=True) #城市id/拼音
    location_name = db.StringProperty(required=True) #城市/名称
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty(required=True)
    length = db.IntegerProperty(required=True)
    where = db.StringProperty() #地点
    geo_point = db.StringProperty() #坐标
    create_at = db.DateTimeProperty(required=True) # 时间戳

    @staticmethod
    def getDbevents(location_id, category, length=None):
        """
        从数据库查询 Dbevents
        """

        query = db.Query(Dbevent)
        query.filter('location_id =', location_id) #地点
        if category != 'all': #类别
            query.filter('category =', 'event.' + category)
        if isinstance(length, int) and length > 0: #活动长度
            query.filter('length <=', length)

        dbevents = query.fetch(limit=1000)
        if len(dbevents) == 0:
            db.put(SyncQueue(key_name=location_id, location_id=location_id))
        return dbevents

    def parse_event(self):
        """转换豆瓣数据模型到iCal数据模型"""
        event = Event()
        event.add('summary', self.title)
        desc = self.summary
        if isinstance(self.participants, int):
            desc += '\n\n' + u'参与人数 %d, 感兴趣人数 %d' \
                    %(self.participants, self.wishers)
        desc += '\n\n' + self.alternate_link
        event.add('DESCRIPTION', desc)
        #event.add('dtstart', self.start_time)
        event['dtstart'] = datetime.strftime(
            get_utc_datetime(self.start_time),
            '%Y%m%dT%H%M%SZ'
            )
        #event.add('dtend', self.end_time)
        event['dtend'] = datetime.strftime(
            get_utc_datetime(self.end_time),
            '%Y%m%dT%H%M%SZ'
            )
        event.add('STATUS', 'CONFIRMED')
        location = self.where
        if self.geo_point != None:
            location += u' @(%s)' %self.geo_point
        event.add('location', location)
        #event.add('dtstamp', datetime.now())
        event['dtstamp'] = datetime.strftime(self.create_at, '%Y%m%dT%H%M%SZ')
        event['uid'] = self.id
        return event

    def isMoreThenAWeek(self):
        """活动距今时间是否大于一周了"""
        delta = datetime.utcnow() - get_utc_datetime(self.end_time)
        return delta.days > 7

    @staticmethod
    def updateDb(location_id):
        """更新日历中活动"""
        dbevents = []
        start = 1
        max = config['sync']['max']
        fetch_page_count = config['sync']['fetch_page_count']

        # 当出现类型筛选时候
        while len(dbevents) < max:
            try:
                xml = fetchEvent(location_id,
                                 max=fetch_page_count,
                                 start=start)
            except GetDoubanDataError, e1:
                logging.error(u'获取数据超时了,先存一些')
                break
            except OverQuotaError, e2:
                logging.error(u'url fetch 中断，限额了')
                break
            dbevents_new = Dbevent.xml2dbevents(xml)
            dbevents += dbevents_new
            if len(dbevents_new) < fetch_page_count: # 到最后一页了
                break
            start += fetch_page_count
        try:
            db.put(dbevents)
        except OverQuotaError, e:
            logging.error(u'更新数据库中断，限额了')
        return len(dbevents)

    @staticmethod
    def deleteDb(location_id):
        """删除结束30天的活动"""
        while True:
            query = db.Query(Dbevent)
            query.filter('location_id =', location_id)
            query.filter('end_time <',
                         datetime.utcnow() - timedelta(days=30))
            dbevents = query.fetch(1000)
            if len(dbevents) == 0:
                break
            db.delete(dbevents)
        return len(dbevents)

    @staticmethod
    def xml2dbevents(xml):
        """使用beautifulsoup转换html到Dbevent"""
        soup = BeautifulStoneSoup(xml)
        entrys = soup.findAll('entry')
        dbevents = [] #FIXME 名字修改
        for entry in entrys:
            try:
                dbevents.append(Dbevent.entry2dbevent(entry))
            except Exception, e:
                logging.error(e)
                continue
        return dbevents

    @staticmethod
    def entry2dbevent(entry):
        """
        转换entry xml到dbevent
        """

        self_link = str(entry.find('id').string)
        id = int(self_link.split('/')[-1])
        title = unicode(entry.title.string)
        category = entry.category['term'].split('#')[-1]
        alternate_link = 'http://www.douban.com/event/%d/' %id
        summary = unicode(entry.summary.string) #.replace(r'\n', '</br>')
        content = unicode(entry.content.string)

        if entry.find('db:attribute',
                      attrs={'name':'invite_only'}).string == 'yes':
            invite_only = True
        else:
            invite_only = False
        if entry.find('db:attribute',
                      attrs={'name':'invite_only'}).string == 'yes':
            can_invite = True
        else:
            can_invite = False
        participants = int(entry.find('db:attribute',
                                      attrs={'name':'participants'}).string)
        wishers  = int(entry.find('db:attribute',
                                      attrs={'name':'wishers'}).string)
        album  = int(entry.find('db:attribute',
                                      attrs={'name':'album'}).string)
        location  = entry.find('db:location')
        location_id = location['id']
        location_name = unicode(location.string)
        start_time = iso8601.parse_date(entry.find('gd:when')['starttime'])
        end_time = iso8601.parse_date(entry.find('gd:when')['endtime'])
        where = entry.find('gd:where')['valuestring']

        length = end_time - start_time
        length = length.days * 24 + length.seconds / 60 /60

        dbevent = Dbevent(
            key_name=str(id),
            id=id,
            title=title,
            self_link=self_link,
            alternate_link=alternate_link,
            category=category,
            summary=summary,
            content=content,
            participants=participants,
            wishers=wishers,
            location_id=location_id,
            location_name=location_name,
            start_time=start_time,
            end_time=end_time,
            length=length,
            where=where,
            create_at=datetime.now(),
            )

        geo_point = entry.find('georss:point')
        if geo_point != None:
            dbevent.geo_point = unicode(geo_point.string)

        return dbevent

# vim: set ft=python:
