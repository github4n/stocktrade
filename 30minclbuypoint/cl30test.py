#!/usr/bin/env python
# -*- coding:utf-8 -*-

from multiprocessing.pool import ThreadPool
import tushare as ts

import pymongo
import json

class sharp:
    """
    30分钟底分型判断
    """

    def get30Kdata(self,code):
        return ts.get_hist_data(code, ktype='30')

    def sharptype(self,code):
        df = self.get30Kdata(code).head(3)

        # conn = pymongo.MongoClient('192.168.222.188', port=27017)


if __name__ == '__main__':
    sharp = sharp()
    sharp.sharptype('000798')