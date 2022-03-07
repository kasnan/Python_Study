# -*- coding: euc-kr -*-

import os
import time
import pyupbit
from collections import deque
from multiprocessing import Process

import BTget
import getCurrentState
global idx
#�ֹ��� �ʴ� 8ȸ, �д� 200ȸ / �ֹ� �� ��û�� �ʴ� 30ȸ, �д� 900ȸ ��� �����մϴ�.
#����Ʈ �ŷ�������� �� �ֹ��ݾ��� 0.05%

# ����Ʈ access key, secret key ����
upbit_access = "GxSdhgc2FodHTpSKKlwGmUWBUDD3fUzH5HcESvc6"
upbit_secret = "ri1rd0AjgTLVN99o3X1XxySRBj23uxv9Hp0ROqdu"

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
            return int(0), int(0)
# �ż� �ֹ�
def buy_order(ticker, volume):
    try:
        while True:
            buy_result = upbit.buy_market_order(ticker, volume)
            if buy_result == None or 'error' in buy_result:
                print("�ż� �� �ֹ�")
                time.sleep(1.5)
            else:
                print(ticker+", "+volume+"�ż�")
                BTget.write_exc(ticker+"�� "+volume+"��ŭ �ż� �Ϸ�","BuyCoin")
                return buy_result
    except:
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
    except:
        print("�ŵ� �ֹ� �̻�")

# ���� �ɺ� �ϳ��� �޾ƿͼ� �̵���ռ� ���� �� �ż� ���� Ž��
def get_ticker_ma(ticker, unitvolume):  

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

    coin_check = get_balance_wallet(ticker) # ���� ���� �ϰ� �ִ��� üũ
    if coin_check == (0,0):
        flag = 0
    avg_price = coin_check[0]   # �ż� ��հ�
    balance = coin_check[1]     # ���� ���� ����

    
    print(ticker + '�ü� ���� ��')
    if curr_ma20 <= curr_ma60 and curr_ma60 <= curr_ma120 and buy_target_price <= now_price:
        # ������ŭ �ż�
        volume = round(unitvolume / now_price * 0.995, 4)
        print("1"+volume)
        buy_order(ticker, volume)
        flag = 1

    elif long_volt_target_price <= now_price:
        # ������ŭ �ż�
        volume = round(unitvolume / now_price * 0.995, 4)
        print("2"+volume)
        buy_order(ticker, volume)
        flag = 1

    elif short_volt_target_price >= now_price:
        # ������ŭ �ż�
        volume = round(unitvolume / now_price * 0.995, 4)
        print("3"+volume)
        buy_order(ticker, volume)
        flag = 1
    
    else:
        print("nothing!")
        if flag == 1:
            # ���� ���� ���� ���ͷ� ��� 
            buy_profit = ((now_price - avg_price) / avg_price) * 100
            profit = round(buy_profit, 4)
            # ��� �ż��� ���� 2% ��� �� �ŵ�
            if profit >= 2.0:
                print(f"{tickezr} : ��ǥ�� ���� �� ���� �ŵ�")
                sell_order(ticker, balance)
                flag = 0 
                time.sleep(1) 
            else:
                print("test")
                print(f"���θ�: {ticker}, ���ͷ�: {profit}%" )
                BTget.write_exc("���θ�: {ticker}, ���ͷ�: {profit}%","ProfitReport")
        else:
            print("pass!")
    print("complete")
            

# ���� ����Ʈ���� �̵� ��ռ� �Լ��� �ϳ��� ������ ������
unitvolume = 500000

def mainp(tickers, idx):
    idx = 0
    print(tickers)
    while True:
        try:        
            for i in range(len(tickers)):
                get_ticker_ma(tickers[i+idx],unitvolume)
                time.sleep(0.2)
                print("test")
        except:
            idx = (idx+1)%len(tickers)
            pass