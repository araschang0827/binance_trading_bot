import pandas as pd
import ccxt
import time
import datetime
import pandas_ta as ta
from Module.ETL import *
from Module.indicators import *
import Module.constants as const

##### 2 EMAs and Supertrend indicators #####
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
            test_order = exchange.create_limit_sell_order('BTCUSDT', 0.001, 50000)
            # fetch historical price
            df = pd.DataFrame(exchange.fetch_ohlcv(symbol,timeframe=interval, limit=1000))
            df = ohlcv_data_standarize(df)

            a = 26
            b = 83
            df['5ema'] = EMA(df, a)
            df['20ema'] = EMA(df, a)
            high = pd.Series(df['high'])
            low = pd.Series(df['low'])
            close = pd.Series(df['close'])
            df['super'] = pd.DataFrame(ta.supertrend(high, low, close))['SUPERTd_7_3.0']
            balance = exchange.fetch_balance()["info"]["assets"][6]["walletBalance"]

            # strategy
            if signal == '':
                if df['close'][999]>df['5ema'][999]>df['20ema'][999] and df['super'][998] ==-1 and df['super'][999] == 1:
                    signal = 'BUY'
                    order = exchange.create_market_buy_order('BTCUSDT', 0.001)
                    print('Create a BUY position.')
                    
                elif df['close'][999]<df['5ema'][999]<df['20ema'][999] and df['super'][998] == 1 and df['super'][999] == -1:
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
        
        except Exception:
            print('Something wrong with the code......')
            time.sleep(1)
            continue
        
