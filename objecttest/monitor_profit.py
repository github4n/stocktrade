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
        # for item in conn.mystock.yjbtrade.find({'tradestatus':0}).sort('buytime',pymongo.ASCENDING):
        for item in conn.mystock.yjbtrade.find().sort('buytime', pymongo.DESCENDING).limit(10):

            # print item['buytime']
            df = ts.get_realtime_quotes(item['code'])
            df1 = ts.get_hist_data(item['code']).head(1)

            status = item['detailtype']

            open = df1['open'][0]
            nowprice = df['price'][0]
            profit = (float(nowprice) - float(item['buyprice'])) / float(item['buyprice']) * 100
            nowprofit = (float(nowprice) - float(item['buyprice'])) / float(item['buyprice']) * 100
            maxprofit = (float(item['maxprice']) - float(item['buyprice'])) / float(item['buyprice']) * 100
            # maxprofit = 0
            #已经卖出的股票的收益
            if item['tradestatus']==1:
                profit = (float(item['sellprice'])-float(item['buyprice']))/float(item['buyprice'])*100

            # if profit < 10:
            #     continue
            if(status=='lowopencross0'):

                print '[lowopencross0] ',item['code'],item['name'],item['buytime'],'buy price ',item['buyprice'],'and now price ',nowprice ,'最大收益',round(maxprofit,2),'%','当前收益:',round(nowprofit,2),'%','总收益:',round(profit,2),'%','持股状态:',item['tradestatus']
            if (status == 'highopenlowhigh'):

                print '[highopenlowhigh] ',item['code'],item['name'],item['buytime'],' buy price ', item['buyprice'],'and now price ', nowprice,'最大收益',round(maxprofit,2),'%','当前收益:',round(nowprofit,2),'%','总收益:',round(profit,2),'%','持股状态:',item['tradestatus']

monitor().monitortrade()