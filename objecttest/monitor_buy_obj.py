
#coding=utf-8
import pymongo
import json
import tushare as ts
import time
import easytrader as et

class buyMonitor:
    #佣金宝登录
    useryjb = et.use('yjb')
    useryjb.prepare('yjb.json')

    #最大股票个数
    maxstockcount = 6

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
                    if (df['pre_close'] > df['open']).bool():
                        self.updateStatus(item['code'],'lowopen',0)

                    # 判断高开
                    if (df['pre_close'] <= df['open']).bool():
                        self.updateStatus(item['code'], 'highopen',0)

                # 低开过零轴（买入）
                if ((item['status'] == 'lowopen') and (df['price'] > df['pre_close']).bool()):
                    buyprice = round(float(df['price'][0]) * 1.02, 2)
                    self.buyStock(df,item['code'].encode("utf-8"),'lowopencross0',item['date'],buyprice)

                #高开低走
                if (item['status'] == 'highopen') and (df['price'] < df['open']).bool():
                    buyprice = round(float(df['price'][0]) * 1.02, 2)
                    self.updateStatus(item['code'], 'highopenlow',0)

                #高开低走再高走（买入）
                if (item['status'] == 'highopenlow') and (df['price'] > df['open']).bool():
                    buyprice = round(float(df['price'][0]) * 1.02, 2)
                    self.buyStock(df,item['code'].encode("utf-8"),'highopenlowhigh',item['date'],buyprice)

                if (item['status'] == 'predeal') and (df['price'] <= item['buyprice'],item['date']):
                    buyprice = round(float(item['buyprice']) * 1.02, 2)
                    self.buyStock(df, item['code'].encode("utf-8"), 'predeal',buyprice)


            except Exception as e:
                print e
                continue


    #买入股票
    def buyStock(self,df,code,type,date,buyprice):
        # 佣金宝购买策略
        buyCount = 100
        #最大数量
        if self.useryjb.balance[0]['asset_balance']/3 > self.useryjb.balance[0]['enable_balance']:
            buyCount = int(self.useryjb.balance[0]['enable_balance'] / (buyprice * 100))*100
        else:
            buyCount = int(self.useryjb.balance[0]['asset_balance']/3 / (buyprice * 100))*100
        if buyCount<=100:
            self.updateStatus(code, 'predeal',buyprice)
            return
        # 买入股票(初期设置100的数量，后期使用策略)
        buyret = self.useryjb.buy(code, price=buyprice, amount=buyCount)
        if buyret['error_no'].encode("utf-8") == '0':
            #修改状态代码
            self.updateStatus(code,type,0,date)
            #插入数据代码
            self.addTrade(df,code,buyCount,type,buyret)
            #print代码
            print '买入'+code+"成功  买入类型："+type
            print '***********************'
            print '***********************'
            print '*****佣金宝买入成功*****'
            print '***********************'
            print '***********************'
            print '========================================'
        else:
            print code,'购买失败'
            print buyret
            print buyret['error_info'].encode("utf-8")
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

    def addTrade(self,df,code,count,type,buyret):
        self.conn.mystock.yjbtrade.insert({"code": code, "buytime": time.strftime("%Y-%m-%d %X", time.localtime()),
                                           "buytype": "zrztb", "detailtype": type,
                                           "buyprice": df['price'][0],
                                           "tradestatus": 0, 'stockcount': count, 'maxprice': df['price'][0],
                                           'buyret': buyret,'lossprice':df['price'][0],'name':df['name'][0]})
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


buyMonitor().monitor()

