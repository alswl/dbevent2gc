#!/usr/bin/env python2
#coding=utf-8

from google.appengine.ext import db

class Event(db.Model):
    """豆瓣同城事件数据模型"""

    id = db.StringProperty(required=True)
    title = db.StringProperty(required=True)
    category = db.StringProperty(required=True) #TODO 关联对象
    summary = db.StringProperty(required=True)
    content = db.StringProperty #TODO
    invite_only = db.BooleanProperty() #需要邀请才能参加
    can_invite = db.BooleanProperty() #允许参加者邀请其友邻来参加
    participants = db.IntegerProperty() #参与人数
    wishers = db.IntegerProperty() #想参加的人
    status = db.StringProperty() #想参加的人
    location = db.StringProperty(required=True) #城市
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty(required=True)
    where = db.StringProperty() #地点

    url = db.LinkProperty()
