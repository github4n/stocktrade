#coding=utf-8
import tushare as ts
import talib as ta
import numpy as np
import pandas as pd
import os,time,sys,re,datetime
import csv
import scipy
import smtplib

df = ts.get_hist_data('600598',start='2014-11-20')
# print df
dflen = len(df.index)
operate = 0
if dflen > 35:
    macd, macdsignal, macdhist = ta.MACD(np.array(df['close']), fastperiod=12, slowperiod=26, signalperiod=9)



    SignalMA5 = ta.MA(macdsignal, timeperiod=5, matype=0)
    SignalMA10 = ta.MA(macdsignal, timeperiod=10, matype=0)
    SignalMA20 = ta.MA(macdsignal, timeperiod=20, matype=0)
    # 在后面增加3列，分别是13-15列，对应的是 DIFF  DEA  DIFF-DEA
    df['macd'] = pd.Series(macd, index=df.index)  # DIFF
    df['macdsignal'] = pd.Series(macdsignal, index=df.index)  # DEA
    df['macdhist'] = pd.Series(macdhist, index=df.index)  # DIFF-DEA
    print df.head(35)
    MAlen = len(SignalMA5)
    # 2个数组 1.DIFF、DEA均为正，DIFF向上突破DEA，买入信号。 2.DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号。
    if df.iat[(dflen - 1), 13] > 0:
        if df.iat[(dflen - 1), 14] > 0:
            if df.iat[(dflen - 1), 13] > df.iat[(dflen - 1), 14]:
                operate = operate + 1  # 买入
    else:
        if df.iat[(dflen - 1), 14] < 0:
            if df.iat[(dflen - 1), 13]:
                operate = operate - 1  # 卖出

    # 3.DEA线与K线发生背离，行情反转信号。
    if df.iat[(dflen - 1), 7] >= df.iat[(dflen - 1), 8] and df.iat[(dflen - 1), 8] >= df.iat[(dflen - 1), 9]:  # K线上涨
        if SignalMA5[MAlen - 1] <= SignalMA10[MAlen - 1] and SignalMA10[MAlen - 1] <= SignalMA20[MAlen - 1]:  # DEA下降
            operate = operate - 1
    elif df.iat[(dflen - 1), 7] <= df.iat[(dflen - 1), 8] and df.iat[(dflen - 1), 8] <= df.iat[(dflen - 1), 9]:  # K线下降
        if SignalMA5[MAlen - 1] >= SignalMA10[MAlen - 1] and SignalMA10[MAlen - 1] >= SignalMA20[MAlen - 1]:  # DEA上涨
            operate = operate + 1

    # 4.分析MACD柱状线，由负变正，买入信号。
    if df.iat[(dflen - 1), 15] > 0 and dflen > 30:
        for i in range(1, 26):
            if df.iat[(dflen - 1 - i), 15] <= 0:  #
                operate = operate + 1
                break
    # 由正变负，卖出信号
    if df.iat[(dflen - 1), 15] < 0 and dflen > 30:
        for i in range(1, 26):
            if df.iat[(dflen - 1 - i), 15] >= 0:  #
                operate = operate - 1
                break

#operate_array.append(operate)
#df_Code['MACD'] = pd.Series(operate_array, index=df_Code.index)