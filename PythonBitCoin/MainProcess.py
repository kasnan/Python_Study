# -*- coding: euc-kr -*-

import os
import time
from numpy import double
import datetime
import sys

import pyupbit
from collections import deque
from multiprocessing import Process

import backtest
import BTget
import getCurrentState
global idx
#�ֹ��� �ʴ� 8ȸ, �д� 200ȸ / �ֹ� �� ��û�� �ʴ� 30ȸ, �д� 900ȸ ��� �����մϴ�.
#����Ʈ �ŷ�������� �� �ֹ��ݾ��� 0.05%

# ����Ʈ access key, secret key ����

upbit_access = "JFAOs6xtLrOUczDGCSpg06idMIu0dojEjQmZBzDO"
upbit_secret = "iFyJ6xrQogWVxZgPLj3QoAxBPtG47EBRqiWvtz6b"
global flag
flag = 0
# ���� ���� ���� deque ����
ma20 = deque(maxlen=20)
ma60 = deque(maxlen=60)
ma120 = deque(maxlen=120)

# login
upbit = pyupbit.Upbit(upbit_access, upbit_secret)

# �ܰ� ��ȸ krw
def get_balance_krw():    
    balance = upbit.get_balance("KRW")
    return balance
# �ܰ� ��ȸ coin
def get_balance_wallet(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker[4:]:
            balance = b['balance']
            avg_buy_price = b['avg_buy_price']
            return float(avg_buy_price), float(balance)
        else:
            pass
    return int(0), int(0)
# �ż� �ֹ�
def buy_order(ticker, volume):
    try:
        for i in range(4):
            buy_result = upbit.buy_market_order(ticker=ticker, price=volume)
            if buy_result == None or 'error' in buy_result:
                print("�ż� �� �ֹ�")
                time.sleep(1)
            else:
                print(ticker+", "+volume+"�ż�")
                BTget.write_exc(str(ticker+"�� "+volume+"��ŭ �ż� �Ϸ�"),"BuyCoin")
                return buy_result
    except Exception as e:
        print(e)
        print("�ż� �ֹ� �̻�")
# �ŵ� �ֹ�
def sell_order(ticker, volume):
    try:
        while True:
            sell_result = upbit.sell_market_order(ticker, volume)
            if sell_result == None or 'error' in sell_result:
                print(f"{sell_result}, �ŵ� �� �ֹ�")
                time.sleep(1)
            else:
                print(ticker+", "+volume+"�ŵ�")
                BTget.write_exc(ticker+"�� "+volume+"��ŭ �ŵ� �Ϸ�","SellCoin")
                return sell_result
    except Exception as e:
        print(e)
        print("�ŵ� �ֹ� �̻�")

# ���� �ɺ� �ϳ��� �޾ƿͼ� �̵���ռ� ���� �� �ż� ���� Ž��
def get_ticker_ma(ticker, unitvolume, mode):  

    '''get_ohlcv �Լ��� ��/�ð�/����/����/�ŷ����� DataFrame���� ��ȯ�մϴ�'''
    df = pyupbit.get_ohlcv(ticker, interval='day', count=21) # �Ϻ� ������ ������ ����
    ma20.extend(df['close'])    # ma20 ������ ���� �ֱ�
    ma60.extend(df['close'])    # ma60 ������ ���� �ֱ�
    ma120.extend(df['close'])   # ma120 ������ ���� �ֱ�
    curr_ma20 = sum(ma20) / len(ma20)       # ma20�� ���ؼ� ������ = 20�ϼ� �̵����
    curr_ma60 = sum(ma60) / len(ma60)       # ma60�� ���ؼ� ������ = 60�ϼ� �̵����
    curr_ma120 = sum(ma120) / len(ma120)    # ma20�� ���ؼ� ������ = 120�ϼ� �̵����

    now_price = pyupbit.get_current_price(ticker)       # ������ ���簡
    open_price = df['open'][-1]                 # ���� �ð� ���ϱ�
    buy_target_price = open_price + (open_price * 0.015) # ��ǥ�� = ���� �ð� ���� 2���� �̻� ��� �ݾ�
    long_volt_target_price, short_volt_target_price = getCurrentState.cal_target(ticker)

    tick, scale = getCurrentState.cal_tickscal(ticker)

    coin_check = get_balance_wallet(ticker) # ���� ���� �ϰ� �ִ��� üũ
    avg_price = coin_check[0]   # �ż� ��հ�
    balance = coin_check[1]     # ���� ���� ����

    if avg_price == 0 and balance == 0:
        flag = 0
    else:
        flag = 1
    timenow = str(datetime.datetime.now())
    print("(����ð� : "+timenow+")")
    print(ticker + '�ü� ���� ��')

    # ������ŭ �ż�

    volume = round(unitvolume * 0.995, scale)
    if flag == 0 and (mode == 'b' or mode == 'n'):
        if long_volt_target_price <= now_price and flag == 0:
            buy_order(ticker, volume)
            BTget.write_exc("���θ�: {}, ���Է�: {}%".format(ticker, volume),"BuyCoin")
            flag = 1

        elif short_volt_target_price >= now_price and flag == 0:
            buy_order(ticker, volume)
            BTget.write_exc("���θ�: {}, ���Է�: {}%".format(ticker, volume),"BuyCoin")
            flag = 1
    
        elif curr_ma20 <= curr_ma60 and curr_ma60 <= curr_ma120 and buy_target_price <= now_price and flag == 0:
            buy_order(ticker, volume)
            BTget.write_exc("���θ�: {}, ���Է�: {}%".format(ticker, volume),"BuyCoin")
            flag = 1
        pass
    elif flag == 1 and (mode == 's' or mode == 'n'):
        if flag == 1:
            # ���� ���� ���� ���ͷ� ��� 
            buy_profit = ((now_price - avg_price) / avg_price) * 100
            profit = round(buy_profit, 4)
            # ��� �ż��� ���� 0.5% ��� �� �ŵ�
            if profit >= 2.5:
                print(f"{ticker} : ��ǥ�� ���� �� ���� �ŵ�")
                sell_order(ticker, balance)
                BTget.write_exc("���θ�: {}, �Ǹŷ�: {}%".format(ticker, balance),"SellCoin")
                flag = 0
                if mode == 's':
                    sys.exit()
                return 0 
            else:
                print("���θ�: {}, ���ͷ�: {}%".format(ticker, profit))
                BTget.write_exc("���θ�: {}, ���ͷ�: {}%".format(ticker, profit),"ProfitReport")
                flag = 0
                return 0
        else:

            print("Nothing!!")
            return 0
            
# ���� ����Ʈ���� �̵� ��ռ� �Լ��� �ϳ��� ������ ������
def mainp(tickers, idx, mode):
    idx = 0
    
    while True:
        try:
            unitvolume = 500000
            for i in range(len(tickers)):
                print("================================================")
                index = (i+idx)%len(tickers)
                get_ticker_ma(tickers[index],unitvolume, mode)
                
                time.sleep(0.7)
                os.system('cls')
        except Exception as e:
            idx = (idx+1)%len(tickers)
            print(e)
            print("pass")
            pass