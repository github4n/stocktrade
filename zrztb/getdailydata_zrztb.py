#coding=utf-8
import pymongo
import json
import tushare as ts
import time
#step1
#获取每天全部A股日数据
#
#

conn = pymongo.MongoClient('192.168.222.188', port=27017)
df = ts.get_today_all()
conn.mystock.todaydata.remove()
conn.mystock.todaydata.insert(json.loads(df.to_json(orient='records')))
