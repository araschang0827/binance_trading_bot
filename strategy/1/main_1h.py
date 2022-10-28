from shutil import ExecError
import pandas as pd
import ccxt
import time
import datetime

symbol = 'BTCUSDT'
interval = '1h'

def ATR(DF, period=14):
    df = DF.copy()
    df['H-L'] = df['high'] - df['low']
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].ewm(span=period, min_periods=period).mean()
    return df['ATR']

# initiate A&A Bot
exchange = ccxt.binanceusdm({
    'apiKey': 'qnWZgAfFaeofQLVCysgdcG2tjKuD7aDzCuk7IHT7hHRAWy9vQXQsVsotPup43M7N',
    'secret': 'zpqxPiAFtTIrsnoOQn8dlldeFgCb5XEe7vaA0FO0hVxeu0eGWOyECghwEFwQXvGw',
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
        df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        df['time'] = pd.to_numeric(df['time'])
        df['time'] = df['time'] / 1000
        for i in range(len(df.index)):
            df['time'][i] = datetime.datetime.fromtimestamp(df['time'][i])
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['close'] = pd.to_numeric(df['close'])
        df['volume'] = pd.to_numeric(df['volume'])

        a = 40
        b = 47
        c = 13
        df['5ema'] = df['close'].ewm(com=a, min_periods=a).mean()
        df['20ema'] = df['close'].ewm(com=b, min_periods=b).mean()
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
