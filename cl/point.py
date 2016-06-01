#coding=utf-8
import pymongo
import json
import tushare as ts
import time
#step1

conn = pymongo.MongoClient('192.168.222.188', port=27017)
df = ts.get_hist_data('600598')

print df.index

# print json.loads(df.to_json(orient='records'))


# conn.mystock.dayline_temp.remove()
# conn.mystock.dayline_temp.insert(json.loads(df.to_json(orient='records')))
# for item in conn.mystock.dayline_temp.find():
#     print item