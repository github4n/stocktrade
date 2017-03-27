#coding=utf-8
import tushare as ts
import pymongo

from multiprocessing.pool import ThreadPool

class fenxing:
    """分型的判断及属性的填充"""

    #分型类型：low——底分型  high——顶分型
    fenxingtype ='low'
    maxprice=100
    conn = pymongo.MongoClient('192.168.222.188', port=27017)
    #是否笔结束的分型
    isok = 0

    def __init__(self,type,isok):
        self.fenxingtype = type
        self.isok = isok


    #判断分型的方法
    def isfenxing(self,df,code,day):
        #底分型判断条件
        if (df['high'][day]>df['high'][day+1]<df['high'][day+2])&(df['low'][day] > df['low'][day+1] < df['low'][day+2]):
            # print '底分型成立',code
            #底分型右侧收盘高于左侧最高点
            # if df['close'][day] >= df['high'][day+2] and df['ma5'][day] < df['ma20'][day] and df['p_change'][day+1]>0 and df['ma5'][day]>df['ma5'][day+1]and df['volume'][day]>df['volume'][day+1]:
            #     obj = self.isfenxing( df, code, day+1)
            #     if obj.fenxingtype == 'down':
            #         print code,'底分型确认',day
            #         print df['p_change'][day-1]
            # if (df['p_change'][0]>2):
                # print '分型第二天上涨！！'
            return fenxing('low',1)


        #顶分型判断条件
        if(df['high'][day] < df['high'][day+1] > df['high'][day+2])&(df['low'][day] < df['low'][day+1] > df['low'][day+2]):
            # print '顶分型成立',code
            return fenxing('high',1)

        if (df['high'][day] < df['high'][day + 1] < df['high'][day + 2]< df['high'][day + 3]< df['high'][day + 4]) & (df['low'][day] < df['low'][day + 1] < df['low'][day + 2]< df['low'][day + 3]< df['low'][day + 4]):
            # print '下降趋势段',code
            return fenxing('down',0)

        if (df['high'][day] > df['high'][day + 1] > df['high'][day + 2]) & (df['low'][day] > df['low'][day + 1] > df['low'][day + 2]):
            # print '上升趋势段',code
            return fenxing('up', 0)

        return fenxing('test', 2)
    #day 为底分型最右侧k线距离今天的日期数
    def monitor(self,code,day):
        try:
            df = ts.get_hist_data(code, ktype='D')

            fenxing = self.isfenxing(df, code, day)
            if fenxing.fenxingtype == 'low':
                # print '底分型',code
                #底分型确认
                # if df['close'][day-1] > df['high'][day]:
                    #待调整
                    # if df['low'][day-1]>df['low'][day]:
                        #底分型缩量？
                        if df['volume'][day+2]>df['volume'][day+1]:
                            #右肩为光头阳线
                            ht = (df['high'][day]-df['close'][day])/df['close'][day]
                            # 右肩涨幅超过2%？
                            # print code,ht,df.index[day+1]
                            print df['p_change'][day]
                            if ht<0.01 and df['p_change'][day] > 2:
                            # if ht < 0.01:
                                print code,' ',df.index[day-1],'底分型确认买入,第二天',df.index[day-2],'涨幅: ', df['p_change'][day-2]
            #以下方法输入1表示从今天前一天算起，输入0表示从今天算起
            # for i in range(1,20):
            #     qushi = self.isfenxing(df,code,i)
            #     if qushi.fenxingtype == 'down':

            #如果是底分型，判断前面是否为下降趋势段
            #如果是下降趋势，判断次级别走势
            #，则可以买入
        except Exception as e:
            print e

    def proxy(self,code):
        for i in range(2, 20):
            self.monitor(code,i)

    def monitorthread(self):
        stock_codes = []
        for item in self.conn.mystock.todaydata.find():

            stock_codes.append(item['code'])
        pool = ThreadPool(40)
        pool.map(self.proxy, stock_codes)

# fenxing('',0).monitor('002703',2)
fenxing('',0).monitorthread()

