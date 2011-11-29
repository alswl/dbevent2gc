#!/usr/bin/env python2
#coding=utf-8

from google.appengine.ext import db

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
