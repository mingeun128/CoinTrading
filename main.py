import time
import pyupbit
import datetime
import numpy as np
import requests
import json

"""실시간 테스트용 클래스"""
class Test:
    def __init__(self):
        self.krw = 1000000
        self.coin = 0
    def __init__(self, krw):
        self.krw = krw
        self.coin = 0
    def get_balance(self, ticker): # 종목은 정해져있다고 가정 - 20220219 mgkim
        if ticker == 'KRW':
            return self.krw
        else:
            return self.coin
    def buy_market_order(self, ticker):
        current_coin = get_current_price(ticker)
        self.coin = (self.krw * 0.9995) / current_coin # 수수료를 고려
        self.krw = 0
    def sell_market_order(self, ticker):
        current_coin = get_current_price(ticker)
        self.krw = (self.coin * 0.9995) * current_coin
        self.coin = 0

"""업비트 API KEY"""
access = ""
secret = ""

"""매매 조건"""
buy_perc = 0.01  # 시작가 대비 1% 오르면 매수
sell_perc = 0.01 # 매수가 대비 1% 오르면 매도(익절)
losscut = -0.01   # 매수가 대비 1% 내리면 losscut 매도(손절)

"""매매 대상 코인"""
ticker = "KRW-XRP"

"""코인 매수 가격"""
buy_coin_price = 0

def get_coins():
    coins = pyupbit.get_tickers(flat="KRW")
    return coins

"""매수 목표가 조회 - 변동성 돌파 전략 사용"""
def get_target_price(ticker, k):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

"""시작 시간 조회(9시)"""
def get_start_time(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

"""시작 가격 조회(일봉 기준)"""
def get_start_price(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_price = df.iloc[0]['open']
    return start_price

"""직전 캔들의 종가 조회(1분봉 기준)"""
def get_previous_candle_close_price(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=1)
    close_price = df.iloc[0]['close']
    return close_price

"""5분 이동 평균선 조회"""
def get_ma5(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=5)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5
'''
"""잔고 조회"""
def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0
'''

"""현재가 조회"""
def get_current_price(ticker):
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def trade(ticker):
    current_coin = get_current_price(ticker)
    start_price = get_start_price(ticker)
    start_price_min1 = get_previous_candle_close_price(ticker)
    l = (current_coin - start_price_min1) / start_price_min1 #구매 전 상승률
    r= 0 #구매 후 변동률
    #krw = get_balance("KRW")
    if test.get_balance(ticker) == 0:
        if test.get_balance('KRW') > 5000 and l >= buy_perc:
            #upbit.buy_market_order("KRW-PLA", krw)
            test.buy_market_order(ticker)
            buy_coin_price = current_coin
            r = (current_coin - buy_coin_price) / buy_coin_price
        elif r <= losscut or r >= sell_perc:
            test.sell_market_order(ticker)

"""로그인"""
#upbit = pyupbit.Upbit(access, secret)
test = Test(krw=1000000)

print("autotrade start")

# 자동매매 시작
while True:
    try:
        #target_price = get_target_price("USDT-BTC", 0.4) #변동성 돌파 전략으로 구한 목표 매수가
                                                            #지금은 사용하지 않는다.
        ma5 = get_ma5("KRW-BTC")
        current_price = get_current_price("KRW-BTC")
        if ma5 < current_price:
            print('TRADE')
            #krw = get_balance("KRW")
            #if krw > 5000:
            #    upbit.buy_market_order("KRW-PLA", krw)
            trade(ticker)
        else:
            print('NOT TRADE')
            if test.get_balance(ticker) > 0:
                test.sell_market_order(ticker)
            #pla = get_balance("PLA")
            #if pla > 3.45:
            #    upbit.sell_market_order("KRW-PLA", pla)
        print("KRW : " + str(test.get_balance('KRW')))
        print("XRP : " + str(test.get_balance(ticker)))
        print("TOTAL : " + str((test.get_balance(ticker) * get_current_price(ticker) + test.get_balance('KRW'))))
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
