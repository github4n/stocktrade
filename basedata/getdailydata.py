#coding=utf-8
import pymongo
import json
import tushare as ts
import time

#获取每天日数据
#
#

conn = pymongo.MongoClient('192.168.222.188', port=27017)

for item in conn.mystock.monitor_weakhardencode.find():
    ts.get_h_data(item['code'])
