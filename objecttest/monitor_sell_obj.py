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
class sellMonitor:
    conn = pymongo.MongoClient('192.168.222.188', port=27017)
    user_sell = et.use('yjb')
    user_sell.prepare('yjb.json')
    today = time.strftime("%Y-%m-%d", time.localtime())
    def deal(self):
        conn = self.conn
        for item in conn.mystock.yjbtrade.find():

            try:
                df = ts.get_realtime_quotes(item['code'])
                # 取得开始时间开始的最大值
                starttime = item['buytime'].split(' ')[0]


                # 最大值需要替换前面程序
                maxprice = round(float(item['maxprice']), 2)
                nowprice = round(float(df['price'][0]), 2)
                preclose = round(float(df['pre_close'][0]), 2)
                lossprice = round(float(df['low'][0]), 2)
                #如果当天，更新最大价格
                if starttime == self.today:
                    # 更新最大收益价格值
                    if (nowprice > maxprice):
                        conn.mystock.yjbtrade.update({'code': item['code'],'buytime':item['buytime']}, {'$set': {'maxprice': nowprice}})
                    # 更新最低价格
                    if (nowprice < lossprice):
                        conn.mystock.yjbtrade.update({'code': item['code'],'buytime':item['buytime']}, {'$set': {'lossprice': lossprice}})
                    continue

                # 更新最大收益价格值
                if (nowprice > maxprice):
                    conn.mystock.yjbtrade.update({'code': item['code'],'buytime':item['buytime']}, {'$set': {'maxprice': nowprice}})

                # 当前收益
                profit = round((float(nowprice) - float(item['buyprice'])) / float(item['buyprice']) * 100, 2)
                # 最大收益
                maxprofit = round((float(maxprice) - float(item['buyprice'])) / float(item['buyprice']) * 100, 2)

                # 当天收益
                todayprofit = round((float(nowprice) - float(preclose)) / float(preclose) * 100, 2)

                # 坑爹的卖出价格计算
                sellprice = round(float(nowprice) * 0.98, 2)

                #可以卖出标识
                if item['tradestatus']==0:

                    # 新增卖出策略保证盈利(1/3卖出策略)
                    sellcount = item['stockcount']
                    if item['tradestatus'] == 0 and self.ifSell(profit, maxprofit, todayprofit, 0):
                        self.sellStock(item['code'].encode("utf-8"), sellprice, sellcount, 'zhisun', item['buytime'])

                    # 止损点为5个点
                    if profit < -5 and todayprofit < 0:
                        print 'sell stock:', item['code']

                        # 计算可买股票数
                        sellcount = item['stockcount']

                        self.sellStock(item['code'].encode("utf-8"),sellprice,sellcount,'zhisun',item['buytime'])

                    # 最大收益大于10个点，止盈点为最大收益回落5个点
                    if maxprofit > 10:

                        # 新增卖出策略保证盈利(1/3卖出策略)
                        sellcount = item['stockcount']
                        if item['tradestatus'] == 0 and self.ifSell(profit, maxprofit, todayprofit, 0):
                            self.sellStock(item['code'].encode("utf-8"), sellprice, sellcount, 'zhisun',item['buytime'])

                        if maxprofit - 5 >= profit:
                            print 'sell stock:', item['code']

                            # 计算可买股票数
                            sellcount = item['stockcount']
                            self.sellStock(item['code'].encode("utf-8"), sellprice, sellcount, 'zhiying',item['buytime'])

                    # 收益低于10，回落4个点止盈
                    if maxprofit <= 10:
                        if maxprofit - 5 >= profit:
                            print 'sell stock:', item['code']

                            # 计算可卖股票数
                            sellcount = item['stockcount']
                            if profit > 0:
                                self.sellStock(item['code'].encode("utf-8"), sellprice, sellcount, 'zhiying',item['buytime'])
                            else:
                                self.sellStock(item['code'].encode("utf-8"), sellprice, sellcount, 'zhisun',item['buytime'])
                        # 最大收益为负数
                        if maxprofit <= 0:
                            if maxprofit + 4 >= profit:
                                print 'sell stock:', item['code']

                                # 计算可卖股票数
                                sellcount = item['stockcount']

                                self.sellStock(item['code'].encode("utf-8"), sellprice, sellcount, 'zhisun',item['buytime'])
            except Exception as e:
                print e
                continue

    #卖出方法
    def sellStock(self,code,sellprice,sellcount,sellType,buytime):
        sellret = self.user_sell.sell(code, price=sellprice, amount=sellcount)
        if sellret['error_no'].encode('utf-8') == '0':
            self.conn.mystock.yjbtrade.update({'code': code, 'tradestatus': 0,'buytime':buytime}, {
                '$set': {'tradestatus': 1, 'sellprice': sellprice, 'selldate': self.today,
                         'selltype': sellType, 'sellret': sellret}})
            print sellret
            print sellret['error_info'].encode("utf-8")
            print '止盈卖出'
            print '账户卖出成功 ', sellcount
            print '========================================'

        else:
            print code
            print sellret
            print sellret['error_info'].encode("utf-8")
            print '卖出错误'
    #卖出策略
    def ifSell(self,profit,maxProfit,todayprofit,daycount):
        #低于最大收益的30%卖出
        if profit <= maxProfit*0.6:
            return 1
        #超过3天收益低于3个点，出局
        if daycount >= 3:
            if maxProfit < 3:
                return 1

        return 0


    def monitor(self):
        while 1:

            if (time.strftime("%H:%M:%S", time.localtime()) < '08:30:00'):
                time.sleep(3600)
            if (time.strftime("%H:%M:%S", time.localtime()) < '09:30:00'):
                continue

            if (time.strftime("%H:%M:%S", time.localtime()) == '11:30:00'):
                time.sleep(5400)
            # 下午3点退出
            if (time.strftime("%H:%M:%S", time.localtime()) > '15:00:00'):
                break
            self.deal()

sellMonitor().monitor()






