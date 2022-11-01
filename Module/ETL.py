import pandas as pd
import datetime

def ohlcv_data_standarize(df):
    '''
    Making ohlcv data clean and able to use.
    '''
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
    return df