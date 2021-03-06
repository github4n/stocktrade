
#coding=utf-8
import pymongo
import tushare as ts
import time
import easytrader as et
from multiprocessing.pool import ThreadPool

class buyMonitor:
    #登录
    user = et.use('xq')
    user.prepare('xq.json')

    #最大股票个数
    maxstockxucount = 6

    #获取mongo链接
    conn = pymongo.MongoClient('192.168.222.188', port=27017)

    # 实际的deal处理
    def deal(self):
        conn = self.conn
        for item in conn.mystock.monitor_weakhardencode.find({"isdeal": 0}):
            try:
                df = ts.get_realtime_quotes(item['code'])
                if (item['status'] == 'init'):
                    # 判断低开
                    if item["close"] > round(float(df['open'][0]), 2):
                        print item['code'], '判断低开价格：', round(float(df['price'][0]), 2),'时间：',time.strftime("%H:%M:%S", time.localtime())
                        self.updateStatus(item['code'],'lowopen',0,item['date'])
                        continue

                    # 判断高开
                    if item["close"] <= round(float(df['open'][0]), 2):
                        print item['code'], '判断高开价格：', round(float(df['price'][0]), 2),'时间：',time.strftime("%H:%M:%S", time.localtime())
                        self.updateStatus(item['code'], 'highopen',0,item['date'])
                        continue

                # 低开过零轴（买入）
                if ((item['status'] == 'lowopen') and (round(float(df['price'][0]), 2) > item["close"])):
                    buyprice = round(float(df['price'][0]) * 1.02, 2)
                    print item['code'], '判断低开过零轴价格：', round(float(df['price'][0]), 2),'时间：',time.strftime("%H:%M:%S", time.localtime())

                    self.buyStock(df,item['code'].encode("utf-8"),'lowopencross0',item['date'],buyprice)
                    continue

                #高开低走
                if (item['status'] == 'highopen') and (df['price'] < df['open']).bool():
                    # buyprice = round(float(df['price'][0]) * 1.02, 2)
                    print item['code'],'判断高开低走价格：',round(float(df['price'][0]), 2),'时间：',time.strftime("%H:%M:%S", time.localtime())

                    self.updateStatus(item['code'], 'highopenlow',0,item['date'])
                    continue

                #高开低走再高走（买入）
                if (item['status'] == 'highopenlow') and (df['price'] > df['open']).bool():
                    buyprice = round(float(df['price'][0]) * 1.02, 2)
                    print item['code'], ' 判断高开低走再高走价格：', round(float(df['price'][0]), 2),'时间：',time.strftime("%H:%M:%S", time.localtime())

                    self.buyStock(df,item['code'].encode("utf-8"),'highopenlowhigh',item['date'],buyprice)
                    continue

                if (item['status'] == 'predeal') and (round(float(df['price'][0]), 2) <= item['buyprice']):
                    # print item['code'], '判断预处理价格：', round(float(df['price'][0]), 2),'时间：',time.strftime("%H:%M:%S", time.localtime())
                    self.buyStock(df, item['code'].encode("utf-8"), 'deal',item['date'],item['buyprice'])
                    continue

            except Exception as e:
                print e
                continue

    #买入股票
    def buyStock(self,df,code,type,date,buyprice):
        # 佣金宝购买策略
        buyCount = 100
        #最大数量
        if self.user.balance[0]['asset_balance'] > self.user.balance[0]['enable_balance']:
            buyCount = int(self.user.balance[0]['enable_balance'] / (buyprice * 100))*100
        else:
            buyCount = int(self.user.balance[0]['asset_balance'] / (buyprice * 100))*100
            print '股票',code,'可买数量为:',buyCount,'时间:',time.strftime("%H:%M:%S", time.localtime())
        if buyCount<100:
            if type!= 'predeal':
                self.updateStatus(code, 'predeal',buyprice,date)
            return
        # 买入股票(初期设置100的数量，后期使用策略)
        #buyCount = 100
        buyret = self.user.adjust_weight(code,10)

        #if buyret['error_no'].encode("utf-8") == '0':
        #修改状态代码
        self.updateStatus(code,type,0,date)
        #插入数据代码
        chengben = (buyprice/1.02*100+10 +  buyprice/1.02/10 + buyprice/1.02/1000)/100
        self.addTrade(df,code,buyCount,type,buyret,chengben)
        #print代码
        print '买入'+code+"成功  买入类型："+type
        print '***********************'
        print '***********************'
        print '*****佣金宝买入成功*****'
        print '***********************'
        print '***********************'
        print '========================================'
        # else:
        #     print code,'购买失败'
        #     print buyret
        #     print buyret['error_info'].encode("utf-8")
    #更新监控数据状态
    def updateStatus(self,code,type,price,date):

        if type =='highopenlow':
            self.conn.mystock.monitor_weakhardencode.update({'code': code, 'status': 'highopen'},{'$set': {'status': type}})

        elif type =='lowopencross0':
            self.conn.mystock.monitor_weakhardencode.update({'code': code, 'status': 'lowopen'},{'$set': {'status': 'lowopencross0', 'isdeal': 1}})

        elif type == 'highopenlowhigh':
            self.conn.mystock.monitor_weakhardencode.update({'code': code, 'status': 'highopenlow'},{'$set': {'status': 'highopenlowhigh', 'isdeal': 1}})

        elif type == 'lowopen' or type == 'highopen':
            self.conn.mystock.monitor_weakhardencode.update({'code': code, 'status': 'init'},{'$set': {'status': type}})

        elif type == 'predeal':
            self.conn.mystock.monitor_weakhardencode.update({'code': code, 'date': date},
                                                            {'$set': {'status': type,'buyprice':price}})
        elif type == 'deal':
            self.conn.mystock.monitor_weakhardencode.update({'code': code, 'date': date},
                                                            {'$set': {'status': type, 'isdeal': 1}})

    def addTrade(self,df,code,count,type,buyret,buyprice):
        self.conn.mystock.yjbtrade.insert({"code": code, "buytime": time.strftime("%Y-%m-%d %X", time.localtime()),
                                           "buytype": "zrztb", "detailtype": type,
                                           "buyprice": buyprice,
                                           "tradestatus": 0, 'stockcount': count, 'maxprice': df['price'][0],
                                           'buyret': buyret,'lossprice':df['price'][0],'name':df['name'][0],'holddays':0})
    #监控器
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
            time.sleep(3)
            # stock_codes = []
            # for item in self.conn.mystock.todaydata.find():
            #     stock_codes.append(item['code'])
            # pool = ThreadPool(5)
            # pool.map(self.multideal, self.conn.mystock.monitor_weakhardencode.find({"isdeal": 0}))


buyMonitor().monitor()

