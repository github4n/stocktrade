#coding=utf-8
import pymongo
import json
import tushare as ts
import time

from multiprocessing.pool import ThreadPool

ISOTIMEFORMAT='%Y-%m-%d %X'

print "%s数据操作"%time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))


def getprestock(code):
    #获取股票日线数据def getprestock(code,startdate):
    df = ts.get_hist_data(code).head(5)
    #当日涨幅在3-6之间
    if 6>df['p_change'][0]>3:
        #当日站上20日线
        if df['close'][0]>df['ma20'][0]:
            #当天放量超过20日均量
            if df['volume'][0]>df['v_ma20'][0]:
                #5日涨跌小于3
                if df['p_change'].sum() < 3:
                    #5日均线小于20日均线
                    if df['ma5'][0]<df['ma20'][0]:
                        print '>>>>>>>>>>>>>>>>'
                        print code
                        print '<<<<<<<<<<<<<<<<'


def duoxiancheng():
    stock_codes = []
    conn = pymongo.MongoClient('192.168.222.188', port=27017)
    for item in conn.mystock.todaydata.find():
        # getprestock(item['code'])
        stock_codes.append(item['code'])
    pool = ThreadPool(40)
    pool.map(getprestock, stock_codes)

duoxiancheng()


