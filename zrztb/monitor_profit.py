#coding=utf-8
import pymongo
import tushare as ts
import re
class monitor:
    """
    监控已经买入的股票，已统计出最佳卖点
    """
    def monitortrade(self):
        conn = pymongo.MongoClient('192.168.222.188', port=27017)
        # for item in conn.mystock.trade.find({'buytime':re.compile('2016-05-27')}):
        for item in conn.mystock.trade.find():

            # print item['buytime']
            df = ts.get_realtime_quotes(item['code'])
            df1 = ts.get_hist_data(item['code']).head(1)

            status = item['detailtype']

            open = df1['open'][0]
            nowprice = df['price'][0]
            profit = (float(nowprice) - float(item['buyprice'])) / float(item['buyprice']) * 100
            #已经卖出的股票的收益
            if item['tradestatus']==1:
                profit = (float(item['sellprice'])-float(item['buyprice']))/float(item['buyprice'])*100


            if(status=='lowopencross0'):

                print item['code'],item['buytime'],'buy price ',item['buyprice'],'and now price ',nowprice ,'收益:',round(profit,2),'%','持股状态:',item['tradestatus']
            if (status == 'highopenlowhigh'):

                print item['code'],item['buytime'],' buy price ', item['buyprice'],'and now price ', nowprice,'收益:',round(profit,2),'%','持股状态:',item['tradestatus']

monitor().monitortrade()