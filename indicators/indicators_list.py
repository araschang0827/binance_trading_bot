def ATR(DF, period=14):
    df = DF.copy()
    df['H-L'] = df['high'] - df['low']
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].ewm(span=period, min_periods=period).mean()
    return df['ATR']


def MACD(DF, fast=12, slow=26, signal=9):
    df = DF.copy()
    df['ma_fast'] = df['close'].ewm(span=fast, min_periods=fast).mean()
    df['ma_slow'] = df['close'].ewm(span=slow, min_periods=slow).mean()
    df['MACD'] = df['ma_fast'] - df['ma_slow']
    df['signal'] = df['MACD'].ewm(span=signal, min_periods=signal).mean()
    return df.loc[:, ['MACD', 'signal']]