import tushare as ts
import pymongo
import json
class store:
    conn = pymongo.MongoClient('192.168.222.188', port=27017)

    def monitor(self, code):
        try:
            df = ts.get_hist_data(code, ktype='W')
            self.conn.mystock.wkline.insert(json.loads(df.to_json(orient='records')))
        except Exception as e:
            print e

    def monitorthread(self):

        for item in self.conn.mystock.todaydata.find():
            self.monitor(item['code'])
store().monitorthread()


