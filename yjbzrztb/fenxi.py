
#coding=utf-8
import pymongo
import json
import tushare as ts
import time








class fenxi:
    def main(self):
        conn = pymongo.MongoClient('192.168.222.188', port=27017)
        count = 0
        for item in conn.mystock.monitor_sy.find():
            if 1>item['shouyi']>0:
                count+=1
                print item
        print count

fenxi().main()