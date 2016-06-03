#coding=utf-8
import pymongo
import json
import tushare as ts
import time
import easytrader as et

"""
监控所有已经购买的股票，到达止损或者止盈，卖出
"""

conn = pymongo.MongoClient('192.168.222.188', port=27017)
user = et.use('xq')
user.prepare('xq.json')

flag = 1
while flag:
    if(time.strftime("%H:%M:%S", time.localtime())< '09:30:00'):
        continue

    if(time.strftime("%H:%M:%S", time.localtime())== '11:30:00'):
        time.sleep(5400)
    #下午3点退出
    if (time.strftime("%H:%M:%S", time.localtime()) == '15:00:00'):
            break

    for item in conn.mystock.trade.find({"tradestatus":0}):

        try:
            df = ts.get_realtime_quotes(item['code'])
            #取得开始时间开始的最大值
            starttime = item['buytime'].split(' ')[0]
            # df1 = ts.get_h_data(item['code'],start=starttime)['high']
            # maxprice = df1.max()
            maxprice = round(item['maxprice'],2)
            nowprice = df['price'][0]
            profit = round((float(nowprice) - float(item['buyprice'])) / float(item['buyprice']) * 100,2)

            maxprofit = round((float(maxprice) - float(item['buyprice'])) / float(item['buyprice']) * 100,2)

            #止损点为5个点
            if profit < -5:
                print 'sell stock:', item['code']
                user.sell(item['code'], nowprice * 0.8, item['count'])
                conn.mystock.trade.update({'code': item['code']}, {'$set': {'tradestatus': 1, 'sellprice': nowprice,'selldate': time.strftime("%Y-%m-%d",time.localtime())}})

            #止盈点为最大收益回落5个点
            if maxprofit -5 >= profit:
                print 'sell stock:',item['code']
                user.sell(item['code'],nowprice*0.8,item['count'])
                conn.mystock.trade.update({'code': item['code']}, {'$set': {'tradestatus': 1,'sellprice':nowprice,'selldate':time.strftime("%Y-%m-%d", time.localtime())}})

        except Exception as e:
            print e
            continue

        flag = 0

