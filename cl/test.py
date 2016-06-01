#coding=utf-8
import pymongo
import json
import tushare as ts
import time
#妖哥优化201603号 策略实验分析

# 涨跌幅小于1%；
# 换手率小于3%；
# 市净率小于0.85；
# 净资产大于1；
# CCI底背离；
# DDE大单净量从大到小；
# 流通股本小于50亿；
# 股票简称不包含ST；
# 股票市场类型不包含创业板；
# 非停牌；

conn = pymongo.MongoClient('192.168.222.188', port=27017)
df = ts.get_realtime_quotes('002549')
# conn.mystock.trade.insert(
#     {"code": '002549', "buytime": time.strftime("%Y-%m-%d %X", time.localtime()), "buytype": "zrztb",
#      "detailtype": "lowopencross0", "buyprice": df['price'].to_json(orient='records')['price']})

# df.to_json(orient='records')
print df.index
# print df.loc['price'].to_json(orient='records')
print df['price'][0]
