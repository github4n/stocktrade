#coding=utf-8
import pymongo
import json
import tushare as ts
import time
import easytrader as et
import math
"""
涨停板战法介绍
经观察，当天放量涨停第二天高开，
之后上涨的概率极大，
顾加以测试
leeyas by 2016-08-05 22:40
"""
class monitor_ztb:
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    today = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
    conn = pymongo.MongoClient('192.168.222.188', port=27017)
    def deal(self):
        conn = self.conn
        conn.mystock.monitor_sy.remove()
        for item in conn.mystock.todaydata.find():
           self.dealOne(item['code'])
    def dealOne(self,code):
        #获取某一股票的历史数据
        df = ts.get_hist_data(code)
        count = len(df)
        df['num'] = self.getArr(count)
        df['date'] = df.index
        df['code'] = code
        #判断涨停板及放量情况


        #现在无法判断前一个交易日和当天的量能比较及后一天交易日开盘情况
        conn = self.conn
        conn.mystock.monitor_ztb.remove()
        conn.mystock.monitor_ztb.insert(json.loads(df.to_json(orient='records')))
        items = conn.mystock.monitor_ztb.find()
        for item in items:
            if item['p_change']>9.6:
                #处理头尾数据
                if item['date'] == self.today:
                    continue
                if item['num'] == count-1:
                    continue

                preVol = self.getPreVol(item['num'])
                isPower = self.isPowerr(preVol,item['volume'])
                if isPower:
                    nextOpen = self.nextOpen(item['num'],'open')
                    if nextOpen > item['close']:
                        shouyi = self.shouyi(item['num'])

                        item['shouyi'] = shouyi
                        item['fangliang'] = item['volume']/preVol
                        conn.mystock.monitor_sy.insert(item)
                        print '++++++++++++++++++++'
                        print preVol
                        print '--------------------'
                        print item['volume']
                        print '--------------------'
                        print code
                        print item['date']
                        print '++++++++++++++++++++'


    # 增加行号方法
    def getArr(self, count):
        arr = []
        for i in range(0, count):
            arr.append(i)
        return arr

    #获取前一日的成交量
    def getPreVol(self,num):
        conn = self.conn
        if num == 0:
            print '第一天'
            return 0
        for item in conn.mystock.monitor_ztb.find({'num':num+1}):
            return item['volume']

    #判断是否放量
    def isPowerr(self,vol1,vol2):
        if vol2>vol1*1.5:
            if vol1 == 0:
                return 0
            print '放量倍数：'+str(vol2/vol1)
            return 1
        return 0

    #下一个交易日开盘
    def nextOpen(self,num,type):
        conn = self.conn
        if num == 0:
            print '第一天'
            return 0
        for item in conn.mystock.monitor_ztb.find({'num': num - 1}):
            return item['open']


    def shouyi(self,num):
        conn = self.conn
        if num == 0:
            print '第一天'
            return 0
        for item in conn.mystock.monitor_ztb.find({'num': num - 1}):
            if item['p_change']>0:
                print '上涨' + str(item['p_change'])
            else:
                print '下跌' + str(item['p_change'])
            return item['p_change']
monitor_ztb().deal()