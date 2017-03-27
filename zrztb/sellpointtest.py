#coding=utf-8
import pymongo
import tushare as ts
import re
class seller:
    """
    """
    def monitortrade(self):
        conn = pymongo.MongoClient('192.168.222.188', port=27017)
        conn.mystock.monitor_weakhardencode.remove({"date":'2016-06-13'})

seller().monitortrade()