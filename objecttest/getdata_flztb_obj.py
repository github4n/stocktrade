#
# #coding=utf-8
# import pymongo
# import json
# import tushare as ts
# import time
#
# class dataDeal:
#     conn = pymongo.MongoClient('192.168.222.188', port=27017)
#
#     def deal(self):
#         df = ts.get_today_all()
#         self.conn.mystock.todaydata.remove()
#         self.conn.mystock.todaydata.insert(json.loads(df.to_json(orient='records')))
#         df = df[df.changepercent>9.6]
#         #当天成交量
#         print '------------------------'
#         for code in df.code:
#             df1 = ts.get_hist_data(code).head(2)
#             if len(df1) ==2:
#                 vol1 = df1['volume'].values[0]
#                 vol2 = df1['volume'].values[1]
#
#                 if vol1>vol2*1.5:
#                     print code
#                     print '放量上涨'
#                     item = self.conn.mystock.todaydata.find_one({'code':code})
#                     print item
#                     self.insertData(item)
#                 print '================='
#         conn = self.conn
#
#     #插入方法
#     def insertData(self,item):
#         inserttime = time.strftime("%Y-%m-%d", time.localtime())
#         count = self.conn.mystock.monitor_weakhardencode.find({'code': item['code'], 'isdeal': 0}).count()
#         type = 'flztb'
#         if count > 0:
#             type = 'flzrztb'
#         insertdata = {
#             "volume": item["volume"],
#             "code": item["code"],
#             "name": item["name"],
#             "nmc": item["nmc"],
#             "turnoverratio": item["turnoverratio"],
#             "pb": item["pb"],
#             "changepercent": item["changepercent"],
#             "trade": item["trade"],
#             "high": item["high"],
#             "amount": item["amount"],
#             "low": item["low"],
#             "settlement": item["settlement"],
#             "open": item["open"],
#             "mktcap": item["mktcap"],
#             "per": item["per"],
#             "status": "init",
#             "date": inserttime,
#             "isdeal": 0,
#             "type": type
#         }
#         if count > 0:
#             self.conn.mystock.monitor_weakhardencode.update({'code': item['code'], 'isdeal': 0}, {"$set": insertdata})
#             return
#         # 需要增加macd值和前一天的macd值
#         self.conn.mystock.monitor_weakhardencode.insert(insertdata)
#     def main(self):
#         self.deal()
#         # self.test()
#
#     def test(self):
#         self.conn.mystock.monitor_weakhardencode.remove({'isdeal':0})
#
# dataDeal().main()