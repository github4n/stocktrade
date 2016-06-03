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
today = time.strftime("%Y-%m-%d",time.localtime())
while 1:
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
            if starttime == today:
                continue

            #最大值需要替换前面程序
            maxprice = round(item['maxprice'],2)
            nowprice = df['price']
            #更新最大收益价格值
            if nowprice > maxprice:
                conn.mystock.trade.update({'code': item['code']},{'$set': {'maxprice': nowprice}})

            #当前收益
            profit = round((float(nowprice) - float(item['buyprice'])) / float(item['buyprice']) * 100,2)
            #最大收益
            maxprofit = round((float(maxprice) - float(item['buyprice'])) / float(item['buyprice']) * 100,2)

            sellprice = float(nowprice) * 0.8
            #止损点为5个点
            if profit < -5:
                print 'sell stock:', item['code']
                conn.mystock.trade.update({'code': item['code']}, {'$set': {'tradestatus': 1, 'sellprice': nowprice,'selldate': today}})
                user.sell(item['code'], price=sellprice, amount=item['stockcount'])

            #止盈点为最大收益回落5个点
            if maxprofit -5 >= profit:
                print 'sell stock:',item['code']
                conn.mystock.trade.update({'code': item['code']}, {'$set': {'tradestatus': 1,'sellprice':nowprice,'selldate':today}})
                user.sell(item['code'], price=sellprice, amount=item['stockcount'])

        except Exception as e:
            print e
            continue



