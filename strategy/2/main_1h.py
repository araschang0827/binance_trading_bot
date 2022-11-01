import pandas as pd
import ccxt
import time
import datetime
from Module.ETL import *
from Module.indicators import *
import Module.constants as const

##### Using ATR and 2 Moving Averages #####
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

# basic settings
position = ''
position_info = {}
count = 0
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

        order_qty = exchange.fetch_account_positions()[152]['info']['positionInitialMargin']
        
        
        count += 1
        if count == 1200:
            print(datetime.datetime.now().strftime('%H:%M:%S')+" I'm still running...don't worry...")
            count = 0
        if order_qty == '0':
            cancel = exchange.cancel_all_orders('BTCUSDT')
        
        # strategy
        if order_qty == '0' and datetime.datetime.now().strftime('%M:%S') == '00:00':
            if df['5ema'][999]>df['20ema'][999]:
                signal = 'BUY'
                stop_loss_atr = df['close'][999] - df['ATR'][999]
                stop_profit_atr = df['close'][999] + 2 * df['ATR'][999]
                order = exchange.create_market_buy_order('BTCUSDT', 0.001)
                profit_order = exchange.create_limit_sell_order('BTCUSDT', 0.001, stop_profit_atr)
                loss_order = exchange.create_stop_market_order('BTCUSDT', 'SELL', 0.001, stop_loss_atr)
                print('Create a BUY position.')
                
            elif df['5ema'][999]<df['20ema'][999]:
                signal = 'SELL'
                stop_loss_atr = df['close'][999] + df['ATR'][999]
                stop_profit_atr = df['close'][999] - 2 * df['ATR'][999]
                order = exchange.create_market_sell_order('BTCUSDT', 0.001)
                profit_order = exchange.create_limit_buy_order('BTCUSDT', 0.001, stop_profit_atr)
                loss_order = exchange.create_stop_market_order('BTCUSDT', 'BUY', 0.001, stop_loss_atr)
                print('Create a SELL position.')

        time.sleep(0.5)
    except Exception:
        print('Something wrong with the code......')
        exchange = ccxt.binanceusdm({
            'apiKey': const.binance_future_api_key,
            'secret': const.binance_future_api_secret,
            'enableRateLimit': True,
            'option': {
                'defaultMarket': 'future',
            },
        })
        time.sleep(1)
        continue