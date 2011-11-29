#!/usr/bin/env python2
#coding=utf-8

import logging

from google.appengine.api import urlfetch

apikey = '0a4b03a80958ff351ee10af81c0afd9f'

def fetchEvent(location, category='all', max=50, start=0):
    """从豆瓣api获取xml数据"""
    url = 'http://api.douban.com/event/location/%s?' \
            'type=%s&start-index=%d&max-results=%d&apikey=%s' %(location,
                                                                category,
                                                                start,
                                                                max,
                                                                apikey)
    logging.info('fetch events from douban url: %s'%url)
    result = urlfetch.fetch(url)
    if result.status_code == 200:
        return result.content
    else:
        raise Exception('get events from douban.com failed')

