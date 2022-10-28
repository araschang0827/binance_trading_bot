import datetime
import pandas as pd
import pandas_ta as ta

# 可用interval, ATR繼續優化
# input parameters
symbol = 'ETHUSDT'
interval = '5m'
df = pd.read_csv('/home/arashappy/backtestdata_btc_5m.csv')


df = df.drop(['Unnamed: 0', 'close_time','quote_volume','count','taker_buy_volume','taker_buy_quote_volume','ignore'], axis=1)

df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']

df['date'] = pd.to_numeric(df['date'])
df['date'] = df['date'] / 1000

for i in range(len(df.index)):
    df['date'][i] = datetime.datetime.fromtimestamp(df['date'][i])

# converting str to int
df['open'] = pd.to_numeric(df['open'])
df['high'] = pd.to_numeric(df['high'])
df['low'] = pd.to_numeric(df['low'])
df['close'] = pd.to_numeric(df['close'])
df['volume'] = pd.to_numeric(df['volume'])

import numpy as np

def concat(df1, list1):
    list1 = pd.DataFrame(list1).T
    list1.columns = ['Start', 'End', 'Ratio']
    return pd.concat([df1, list1], axis=0, ignore_index=True)

def ATR(DF, period=14):
    df = DF.copy()
    df['H-L'] = df['high'] - df['low']
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].ewm(span=period, min_periods=period).mean()
    return df['ATR']

def CAGR(DF):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    n = len(df)/(365*288)
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    "function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    vol = df["ret"].std() * np.sqrt(252*78)
    return vol

def sharpe(DF,rf):
    "function to calculate sharpe ratio ; rf is the risk free rate"
    df = DF.copy()
    sr = (CAGR(df) - rf)/volatility(df)
    return sr

def max_dd(DF):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd


ratio = pd.DataFrame([1,1,1,1,1]).T
ratio.columns = ['short', 'long', 'cagr', 'sharpe', 'ratio']
count = 0
high = pd.Series(df['high'])
low = pd.Series(df['low'])
close = pd.Series(df['close'])
df['super'] = pd.DataFrame(ta.supertrend(high, low, close))['SUPERTd_7_3.0']

for a in range(1, 51):
    for b in range(10, 201):

        df['5ema'] = df['close'].ewm(span=a, min_periods=a).mean()
        df['20ema'] = df['close'].ewm(span=b, min_periods=b).mean()
        ret = []
        signal = ''
        transaction = pd.DataFrame([1,1,1]).T
        transaction.columns = ['Start', 'End', 'Ratio']
        trans = []
        start_price = 0

        for i in range(len(df)):

            if signal == '':
                ret.append(0)
                if df['close'][i]>df['5ema'][i]>df['20ema'][i] and df['super'][i-1] ==-1 and df['super'][i] == 1:
                    signal = 'BUY'
                    # Don't touch
                    trans.append(df['date'][i])
                    start_price = df['close'][i]
                
                elif df['close'][i]<df['5ema'][i]<df['20ema'][i] and df['super'][i-1] ==1 and df['super'][i]==-1:
                    signal = 'SELL'
                    # Don't touch
                    trans.append(df['date'][i])
                    start_price = df['close'][i]
                
            elif signal == 'BUY':
                if df['close'][i]<df['5ema'][i]:  # stop profit
                    signal = ''

                    # Don't touch
                    ret.append((df['close'][i]/df['close'][i-1])-1)
                    trans.append(df['date'][i])
                    trans.append((df['close'][i] - start_price)/start_price)
                    transaction = concat(transaction, trans)
                    trans = []
                    start_price = 0
                
                else:
                    # Don't touch
                    ret.append((df['close'][i]/df['close'][i-1])-1)
            
            elif signal == 'SELL':
                if df['close'][i]>df['5ema'][i]:  # normal stop profit
                    signal = ''

                    # Don't touch
                    ret.append((df['close'][i-1]/df['close'][i])-1)
                    trans.append(df['date'][i])
                    trans.append((start_price - df['close'][i])/start_price)
                    transaction = concat(transaction, trans)
                    trans = []
                    start_price = 0

                else:
                    # Don't touch
                    ret.append((df['close'][i-1]/df['close'][i])-1)

        # Don't touch
        ret = pd.DataFrame(ret, columns=['ret'])
        transaction['Ratio'] = 100 * transaction['Ratio']
        transaction = transaction.drop([0])
        sum = transaction['Ratio'].sum()
        tem = pd.DataFrame([a,b,CAGR(ret),sharpe(ret, 0.0343),sum]).T
        tem.columns = ['short', 'long', 'cagr', 'sharpe', 'ratio']
        ratio = pd.concat([ratio, tem], axis=0, ignore_index=True)
        print(count)
        count += 1
ratio = ratio.drop([0])
ratio.to_csv('/home/arashappy/backtest_result_3_5m.csv')