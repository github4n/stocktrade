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

    # 量能量化
    def monitor_vol(self, code):
        try:
            day = 1
            df = ts.get_hist_data(code, ktype='D')
            if df['volume'][day] > df['v_ma20'][day] and df['volume'][day+1] < df['v_ma20'][day+0] and df['volume'][day+2] < \
                    df['v_ma20'][0] and df['volume'][day+3] < df['v_ma20'][day+0] and df['volume'][day+4] < df['v_ma20'][day+0] and \
                            df['volume'][day+5] < df['v_ma20'][day+0]:
                p_change5 = df['p_change'][day-1]+df['p_change'][day-2]+df['p_change'][day-3]+df['p_change'][day-4]+df['p_change'][day-5]
                p_change10 = df['p_change'][day - 1] + df['p_change'][day - 2] + df['p_change'][day - 3] + \
                             df['p_change'][day - 4] + df['p_change'][day - 5]+ df['p_change'][day - 6]+ df['p_change'][day - 7]+ df['p_change'][day - 8]+ df['p_change'][day - 9]+ df['p_change'][day - 10]

                #放量并且是上升趋势
                if df['p_change'][day]>2 and df['high'][day] > df['high'][day + 1] and df['low'][day] > df['low'][day + 1]:
                    if df.index[day]=="2016-10-24" and df['p_change'][day+1]<5:
                        if df['v_ma20'][day]<df['v_ma5'][day]:
                            print code ,"放量上涨"
                    # print code,"日期：",df.index[day],"第二天涨幅",df['p_change'][day-1],"   之后5天涨幅",p_change5,'   之后10天涨幅',p_change10
        except Exception as e:
            print e
    def monitorthread_vol(self):
        stock_codes = []
        for item in self.conn.mystock.todaydata.find():
            stock_codes.append(item['code'])
        pool = ThreadPool(2)
        pool.map(self.monitor_vol, stock_codes)
fenxing('',0).monitorthread_vol()

