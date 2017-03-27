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

# user_sell = et.use('yjb')
# user_sell.prepare('yjb.json')
# while 1:
#     try:
#         df = ts.get_realtime_quotes("000935")
#         nowprice = float(df['price'][0])
#         if nowprice < 27.74:
#             sellret = user_sell.sell("000935", price=26.1, amount=100)
#             print "卖出成功"
#         # else:
#             # print nowprice
#
#         # sellret = user_sell.sell("000935", price=24, amount=100)
#     except Exception as e:
#         print e









