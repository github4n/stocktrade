#coding=utf-8
import pymongo
import json
import tushare as ts
import time
import easytrader as et
import math

"""
监控所有已经购买的股票，到达止损或者止盈，卖出
卖出策略修改（止损5个点，破MA5卖出）
每天统计个股收益，并根据收益计算止损
"""

conn = pymongo.MongoClient('192.168.222.188', port=27017)
user_sell = et.use('yjb')
user_sell.prepare('yjb.json')

today = time.strftime("%Y-%m-%d",time.localtime())
while 1:

    if (time.strftime("%H:%M:%S", time.localtime()) < '08:30:00'):
        time.sleep(3600)
    if(time.strftime("%H:%M:%S", time.localtime())< '09:30:00'):
        continue

    if(time.strftime("%H:%M:%S", time.localtime())== '11:30:00'):
        time.sleep(5400)
    #下午3点退出
    if (time.strftime("%H:%M:%S", time.localtime()) > '15:00:00'):
            break

    for item in conn.mystock.yjbtrade.find({"tradestatus":0}):

        try:
            df = ts.get_realtime_quotes(item['code'])
            #取得开始时间开始的最大值
            starttime = item['buytime'].split(' ')[0]
            if starttime == today:
                continue

            #最大值需要替换前面程序
            maxprice = round(float(item['maxprice']),2)
            nowprice = round(float(df['price'][0]),2)
            preclose = round(float(df['pre_close'][0]),2)

            #更新最大收益价格值
            if (nowprice > maxprice):
                conn.mystock.yjbtrade.update({'code': item['code']},{'$set': {'maxprice': nowprice}})

            #当前收益
            profit = round((float(nowprice) - float(item['buyprice'])) / float(item['buyprice']) * 100,2)
            #最大收益
            maxprofit = round((float(maxprice) - float(item['buyprice'])) / float(item['buyprice']) * 100,2)

            #当天收益
            todayprofit = round((float(nowprice) - float(preclose)) / float(preclose) * 100,2)

            #坑爹的卖出价格计算
            sellprice = round(float(nowprice) * 0.98,2)
            #止损点为5个点
            if profit < -5 and todayprofit < 0:
                print 'sell stock:', item['code']

                #计算可买股票数
                sellcount = item['stockcount']

                sellret = user_sell.sell(item['code'].encode("utf-8"), price=sellprice, amount=sellcount)

                if sellret['error_no'].encode('utf-8')=='0':
                    conn.mystock.yjbtrade.update({'code': item['code'], 'tradestatus': 0}, {
                        '$set': {'tradestatus': 1, 'sellprice': nowprice, 'selldate': today, 'selltype': 'zhisun'}})
                    print sellret
                    print '止损卖出'
                    print '账户卖出成功 ',sellcount
                    print '========================================'
                else:
                    print sellret
                    print sellret['error_info'].encode("utf-8")
                    print '卖出错误'

            #最大收益大于10个点，止盈点为最大收益回落5个点
            if maxprofit > 10:
                if maxprofit -5 >= profit:
                    print 'sell stock:',item['code']

                    # 计算可买股票数
                    sellcount = item['stockcount']

                    sellret = user_sell.sell(item['code'].encode("utf-8"), price=sellprice, amount=sellcount)
                    if sellret['error_no'].encode('utf-8') == '0':
                        conn.mystock.yjbtrade.update({'code': item['code'], 'tradestatus': 0}, {
                            '$set': {'tradestatus': 1, 'sellprice': nowprice, 'selldate': today, 'selltype': 'zhiying','sellret':sellret}})
                        print sellret
                        print sellret['error_info'].encode("utf-8")
                        print '止盈卖出'
                        print '账户卖出成功 ',sellcount
                        print '========================================'

                    else:
                        print sellret
                        print sellret['error_info'].encode("utf-8")
                        print '卖出错误'
            #收益低于10，回落4个点止盈
            if maxprofit <= 10:
                if maxprofit - 4 >= profit:
                    print 'sell stock:', item['code']

                    # 计算可买股票数
                    sellcount = item['stockcount']

                    sellret = user_sell.sell(item['code'].encode("utf-8"), price=sellprice, amount=sellcount)
                    if sellret['error_no'].encode('utf-8') == '0':
                        conn.mystock.yjbtrade.update({'code': item['code'], 'tradestatus': 0}, {
                            '$set': {'tradestatus': 1, 'sellprice': nowprice, 'selldate': today,
                                     'selltype': 'zhiying','sellret':sellret}})
                        print sellret
                        print sellret['error_info'].encode("utf-8")
                        print '止盈卖出'
                        print '账户卖出成功 ', sellcount
                        print '========================================'

                    else:
                        print sellret
                        print sellret['error_info'].encode("utf-8")
                        print '卖出错误'
                # 最大收益为负数
                if maxprofit <= 0:
                    if maxprofit + 3 >= profit:
                        print 'sell stock:', item['code']

                        # 计算可买股票数
                        sellcount = item['stockcount']

                        sellret = user_sell.sell(item['code'].encode("utf-8"), price=sellprice, amount=sellcount)
                        if sellret['error_no'].encode('utf-8') == '0':
                            conn.mystock.yjbtrade.update({'code': item['code'], 'tradestatus': 0}, {
                                '$set': {'tradestatus': 1, 'sellprice': nowprice, 'selldate': today,
                                         'selltype': 'zhiying', 'sellret': sellret}})
                            print sellret
                            print sellret['error_info'].encode("utf-8")
                            print '止盈卖出'
                            print '账户卖出成功 ', sellcount
                            print '========================================'

                        else:
                            print sellret
                            print sellret['error_info'].encode("utf-8")
                            print '卖出错误'



        except Exception as e:
            print e
            continue



