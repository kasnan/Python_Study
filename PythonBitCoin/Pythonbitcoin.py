# -*- coding: euc-kr -*-

import time
import pyupbit
from multiprocessing import Process
from datetime import datetime

import MainProcess
import backtest

current_time = datetime.now()
current_year = current_time.year
current_month = current_time.month

target_year = 0
target_month = 0



# ���� ����Ʈ
tickers = []
# ��ȭ�� �Ÿ� ������ ���� ����Ʈ �����
tickers = pyupbit.get_tickers(fiat="KRW")
lent = len(tickers)
'''
tmplist = backtest.getsorted_hpr(target_year, target_month)

for i in range(len(tmplist)):
    tickerlist_sorted.append(tmplist[i][0])

'''
idx = 0
ticker = ['KRW-STRK']
MainProcess.mainp(ticker, idx, 's')