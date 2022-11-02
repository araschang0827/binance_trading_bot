import sys
sys.path.append('/Users/araschang/Desktop/coding/binance_trading_bot/')
import pandas as pd
import ccxt
import time
import datetime
from Module.ETL import *
from Module.indicators import *
import Module.constants as const

symbol = 'BTCUSDT'
interval = '5m'

# initiate A&A Bot
exchange = ccxt.binanceusdm({
    'apiKey': const.binance_future_api_key,
    'secret': const.binance_future_api_secret,
    'enableRateLimit': True,
    'option': {
        'defaultMarket': 'future',
    },
})

balance = exchange.fetch_balance()["info"]["assets"][6]["walletBalance"]
print(f'USDT Balance: {balance}')
print('Ready to trade......')

# basic settings
signal = ''
while True:
    if int(datetime.datetime.now().strftime('%M'))%5 == 0 and int(datetime.datetime.now().strftime('%S')) == 5:
        try:
            test_cancel = exchange.cancel_all_orders('BTCUSDT')
            test_order = exchange.create_limit_buy_order('BTCUSDT', 0.001, 10000)
            # fetch historical price
            df = pd.DataFrame(exchange.fetch_ohlcv(symbol,timeframe=interval, limit=1000))
            ohlcv_data_standarize(df)

            a = 10
            b = 54
            df['5ema'] = EMA(df, a)
            df['20ema'] = EMA(df, b)
            balance = exchange.fetch_balance()["info"]["assets"][6]["walletBalance"]

            # strategy
            if signal == '':
                if df['close'][999]>df['5ema'][999]>df['20ema'][999]:
                    signal = 'BUY'
                    order = exchange.create_market_buy_order('BTCUSDT', 0.001)
                    print('Create a BUY position.')
                    
                if df['close'][999]<df['5ema'][999]<df['20ema'][999]:
                    signal = 'SELL'
                    order = exchange.create_market_sell_order('BTCUSDT', 0.001)
                    print('Create a SELL position.')

            elif signal == 'BUY':
                if df['close'][999]<df['5ema'][999]:  # stop profit
                    signal = ''
                    order = exchange.create_market_sell_order('BTCUSDT', 0.001)
                    print('STOP PROFIT.')
            
            elif signal == 'SELL':
                if df['close'][999]>df['5ema'][999]:  # normal stop profit
                    signal = ''
                    order = exchange.create_market_buy_order('BTCUSDT', 0.001)
                    print('STOP PROFIT.')
            time.sleep(1)
        
        except Exception as e:
            print(e)
            time.sleep(1)
            continue
        
