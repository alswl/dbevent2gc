#!/usr/bin/env python
#coding=utf-8

# desc: convert utc time
# author: alswl
# date: 2012-02-10

def get_utc_datetime(d):
    """将带时间的datetime转换为utc时间"""
    if d.tzinfo is None:
        return d
    else:
        return d.tzinfo.utcoffset(d) + d.replace(tzinfo=None)
