#coding=utf-8
import pymongo
import json
import tushare as ts
import time

#step2 分析出待监控股票

ISOTIMEFORMAT='%Y-%m-%d %X'

print "%s数据操作"%time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))

conn = pymongo.MongoClient('192.168.222.188', port=27017)

print "获取时间开始%s"%time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))

#更新历史数据的isdeal字段
for item in conn.mystock.monitor_weakhardencode.find({"isdeal":0}):
    conn.mystock.monitor_weakhardencode.update({'isdeal': 0}, {'$set': {'isdeal': 1,'status':'expired'}})
#获取当天全部日数据
df = ts.get_today_all()

startTime = time.strftime(ISOTIMEFORMAT, time.gmtime(time.time()))

print "数据库操作开始时间%s"%startTime

conn.mystock.todaydata.remove()
conn.mystock.todaydata.insert(json.loads(df.to_json(orient='records')))

endtime = time.strftime(ISOTIMEFORMAT, time.gmtime(time.time()))
print "数据库操作结束%s"%endtime

inserttime = time.strftime("%Y-%m-%d", time.localtime())


conn.mystock.todaydata_zrztbmingxi.remove()
#遍历当日所有股票数据，判断涨停数据
for item in conn.mystock.todaydata.find():
    try:
        ztprice = round(float(item['settlement']*1.1), 2)
        #判断涨停逻辑为开票价格*1.1四舍五入
        if item['changepercent']>9.5:
            df = ts.get_today_ticks(item['code'])
            df['code'] = item['code']
            #删除上一只股票的分笔数据
            conn.mystock.todaydata_zrztbmingxi.remove()
            #查询当日分笔数据
            conn.mystock.todaydata_zrztbmingxi.insert(json.loads(df.to_json(orient='records')))

            ztflag = 0
            ztcount = 0
            for stock in conn.mystock.todaydata_zrztbmingxi.find({"code":item['code']}).sort("time",pymongo.ASCENDING):

                #判断涨停价格的时间分布，并回置monitor_weakhardencode表中的状态
                if (stock['price']==ztprice):
                    if(ztflag==0):
                        print "第一笔开板时间为:",stock['time']
                        ztflag = 1

                if(ztflag == 1):
                    if(stock['price']<ztprice):
                        ztcount+=1

                    if (stock['price'] == ztprice):
                        if (stock['type'] == u'买盘'):
                            ztcount+=1

                if(ztcount==100):
                    ztcount += 1
                    print "100，符合最弱涨停板条件",item['code']
                    # 如果是涨停数据，把当天详细数据拿到并存储分析
                    insertdata = {
                        "volume": item["volume"],
                        "code": item["code"],
                        "name": item["name"],
                        "nmc": item["nmc"],
                        "turnoverratio": item["turnoverratio"],
                        "pb": item["pb"],
                        "changepercent": item["changepercent"],
                        "trade": item["trade"],
                        "high": item["high"],
                        "amount": item["amount"],
                        "low": item["low"],
                        "settlement": item["settlement"],
                        "open": item["open"],
                        "mktcap": item["mktcap"],
                        "per": item["per"],
                        "status":"init",
                        "date":inserttime,
                        "isdeal":0
                    }
                    #需要增加macd值和前一天的macd值
                    conn.mystock.monitor_weakhardencode.insert(insertdata)
            if(ztcount>0):
                print "开板个数",ztcount,item['code']
    except Exception as e:
        print e
        continue

#最高价格数据处理
for item in conn.mystock.trade.find({"tradestatus":0}):
    try:
        #取得开始时间开始的最大值
        starttime = item['buytime'].split(' ')[0]
        df1 = ts.get_h_data(item['code'],start=starttime)['high']
        maxprice = df1.max()
        conn.mystock.trade.update({'code': item['code']}, {'$set': {'maxprice': maxprice}})

    except Exception as e:
        print e
        continue