import pandas as pd
import ccxt
import time
import datetime

symbol = 'BTCUSDT'
interval = '5m'

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

# basic settings
signal = ''
while True:
    if int(datetime.datetime.now().strftime('%M'))%5 == 0 and int(datetime.datetime.now().strftime('%S')) == 5:
        try:
            test_cancel = exchange.cancel_all_orders('BTCUSDT')
            test_order = exchange.create_limit_buy_order('BTCUSDT', 0.001, 10000)
            # fetch historical price
            df = pd.DataFrame(exchange.fetch_ohlcv(symbol,timeframe=interval, limit=1000))
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

            a = 10
            b = 54
            df['5ema'] = df['close'].ewm(com=a, min_periods=a).mean() # com or span
            df['20ema'] = df['close'].ewm(com=b, min_periods=b).mean()
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
        
