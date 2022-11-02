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
interval = '1h'

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

signal = ''
while True:
    try:
        # fetch historical price
        df = pd.DataFrame(exchange.fetch_ohlcv('BTCUSDT',timeframe='1h', limit=1000))
        df = ohlcv_data_standarize(df)

        a = 40
        b = 47
        c = 13
        df['5ema'] = EMA(df, a)
        df['20ema'] = EMA(df, b)
        df['ATR'] = ATR(df, period=c)
        balance = exchange.fetch_balance()["info"]["assets"][6]["walletBalance"]

        order_qty = exchange.fetch_account_positions()[152]['initialMargin']
        # strategy
        if signal == '':
            if df['5ema'][999]>df['20ema'][999]:
                signal = 'BUY'
                stop_loss_atr = df['close'][999] - df['ATR'][999]
                stop_profit_atr = df['close'][999] + 2 * df['ATR'][999]
                order = exchange.create_market_buy_order('BTCUSDT', 0.001)
                print('Create a BUY position.')
                
            elif df['5ema'][999]<df['20ema'][999]:
                signal = 'SELL'
                stop_loss_atr = df['close'][999] + df['ATR'][999]
                stop_profit_atr = df['close'][999] - 2 * df['ATR'][999]
                order = exchange.create_market_sell_order('BTCUSDT', 0.001)
                print('Create a SELL position.')

        elif signal == 'BUY':
            if df['close'][999]>stop_profit_atr:  # stop profit
                signal = ''
                order = exchange.create_market_sell_order('BTCUSDT', 0.001)
                print('STOP PROFIT.')

            elif df['close'][999]<stop_loss_atr: # stop loss
                signal = ''
                order = exchange.create_market_sell_order('BTCUSDT', 0.001)
                print('STOP LOSS.')

            else:
                pass
        
        elif signal == 'SELL':
            if df['close'][999]<stop_profit_atr:  # normal stop profit
                signal = ''
                order = exchange.create_market_buy_order('BTCUSDT', 0.001)
                print('STOP PROFIT.')

            elif stop_loss_atr>df['close'][999]:  # stop loss
                signal = ''
                order = exchange.create_market_buy_order('BTCUSDT', 0.001)
                print('STOP LOSS.')

            else:
                pass
        
        time.sleep(3600.1)
    except Exception:
        print('Something wrong with the code......')
        time.sleep(1)
        continue
